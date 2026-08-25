import os

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from app.auth import require_authenticated_user
from app.database import session_scope
from app.models import BillingAccount, CreditTransaction

router = APIRouter(prefix="/api/admin", tags=["admin"])

ADMIN_CREDITS = 100000
ADMIN_TRANSACTION_KIND = "admin_credit"
ADMIN_TRANSACTION_DESCRIPTION = "Créditos administrativos do proprietário"
DEFAULT_CLINIC_OWNER_USER_ID = "user_3IO0iCF2RnRzluAa4NWzKxhjTmJ"


def _configured_owner_user_id() -> str:
    return os.getenv("CLINIC_OWNER_USER_ID", DEFAULT_CLINIC_OWNER_USER_ID).strip()


def _is_configured_owner(user_id: str) -> bool:
    owner_user_id = _configured_owner_user_id()
    return bool(owner_user_id and user_id == owner_user_id)


def _admin_marker(db, user_id: str) -> str | None:
    return db.scalar(
        select(CreditTransaction.id)
        .where(
            CreditTransaction.user_id == user_id,
            CreditTransaction.kind == ADMIN_TRANSACTION_KIND,
            CreditTransaction.description == ADMIN_TRANSACTION_DESCRIPTION,
        )
        .limit(1)
    )


def _any_admin_marker(db) -> str | None:
    return db.scalar(
        select(CreditTransaction.id)
        .where(
            CreditTransaction.kind == ADMIN_TRANSACTION_KIND,
            CreditTransaction.description == ADMIN_TRANSACTION_DESCRIPTION,
        )
        .limit(1)
    )


def _is_legacy_admin_account(account: BillingAccount | None) -> bool:
    return bool(
        account
        and account.plan == "premium"
        and account.subscription_status == "active"
        and account.plan_credits >= ADMIN_CREDITS
    )


def _can_migrate_legacy_admin(db, account: BillingAccount | None) -> bool:
    return bool(not _any_admin_marker(db) and _is_legacy_admin_account(account))


def _has_persisted_admin_access(user_id: str) -> bool:
    if _is_configured_owner(user_id):
        return True

    with session_scope() as db:
        account = db.get(BillingAccount, user_id)
        if account is None:
            return False

        return bool(_admin_marker(db, user_id) or _can_migrate_legacy_admin(db, account))


def _grant_admin_access(user_id: str) -> dict:
    with session_scope() as db:
        account = db.get(BillingAccount, user_id)
        configured_owner = _is_configured_owner(user_id)

        if account is None:
            if not configured_owner:
                raise HTTPException(status_code=403, detail="Vínculo administrativo não encontrado.")
            account = BillingAccount(
                user_id=user_id,
                plan="premium",
                subscription_status="active",
                plan_credits=ADMIN_CREDITS,
                extra_credits=0,
                current_period_end=None,
            )
            db.add(account)
            db.flush()

        marker = _admin_marker(db, user_id)
        can_migrate = _can_migrate_legacy_admin(db, account)
        if not configured_owner and not marker and not can_migrate:
            raise HTTPException(status_code=403, detail="Vínculo administrativo não encontrado.")

        account.plan = "premium"
        account.subscription_status = "active"
        account.plan_credits = max(account.plan_credits, ADMIN_CREDITS)
        account.current_period_end = None

        if not marker:
            db.add(CreditTransaction(
                user_id=user_id,
                kind=ADMIN_TRANSACTION_KIND,
                amount=0,
                plan_balance=account.plan_credits,
                extra_balance=account.extra_credits,
                description=ADMIN_TRANSACTION_DESCRIPTION,
            ))

        return {
            "status": "ok",
            "role": "admin",
            "plan": "premium",
            "premiumActive": True,
            "subscriptionStatus": "active",
            "planCredits": account.plan_credits,
            "extraCredits": account.extra_credits,
            "totalCredits": account.plan_credits + account.extra_credits,
        }


def owner_access_status(session: dict) -> dict:
    user_id = str(session.get("sub") or "").strip()
    if not user_id:
        raise HTTPException(status_code=401, detail="Sessão inválida.")

    try:
        _grant_admin_access(user_id)
    except HTTPException as exc:
        if exc.status_code == 403:
            return {"role": "user", "isAdmin": False}
        raise

    return {"role": "admin", "isAdmin": True}


@router.post("/bootstrap")
def bootstrap_owner_admin(session: dict = Depends(require_authenticated_user)):
    user_id = str(session.get("sub") or "").strip()
    if not user_id:
        raise HTTPException(status_code=401, detail="Sessão inválida.")

    if not _has_persisted_admin_access(user_id):
        raise HTTPException(status_code=403, detail="Acesso administrativo não autorizado.")

    return _grant_admin_access(user_id)
