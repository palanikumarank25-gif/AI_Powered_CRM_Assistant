import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "crm_data.json"


VALID_STATUSES = {
    "New",
    "Contacted",
    "Won",
    "Lost"
}


def load_data():
    """Load CRM data from JSON."""

    with open(
        DATA_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def save_data(data):
    """Save CRM data to JSON."""

    with open(
        DATA_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=2
        )


# =========================================================
# CUSTOMER TOOLS
# =========================================================

def search_customers(query: str):

    data = load_data()

    query = query.strip().lower()

    if not query:
        return []

    results = []

    for customer in data["customers"]:

        searchable_text = " ".join([
            customer["id"],
            customer["name"],
            customer["company"],
            customer["email"]
        ]).lower()

        if query in searchable_text:

            results.append(customer)

    return results


def get_customer_by_id(customer_id: str):

    data = load_data()

    for customer in data["customers"]:

        if customer["id"] == customer_id:

            return customer

    return None


# =========================================================
# DEAL TOOLS
# =========================================================

def get_deals_for_customer(
    customer_id: str
):

    data = load_data()

    return [
        deal
        for deal in data["deals"]
        if deal["customer_id"] == customer_id
    ]


def search_deals(
    min_value: float = 0,
    inactive_days: int = 0,
    status: Optional[str] = None
):

    data = load_data()

    deals = data["deals"]

    if min_value > 0:

        deals = [
            deal
            for deal in deals
            if deal["value"] > min_value
        ]

    if status:

        normalized_status = status.title()

        deals = [
            deal
            for deal in deals
            if deal["status"] == normalized_status
        ]

    if inactive_days > 0:

        cutoff_date = (
            datetime.now().date()
            - timedelta(days=inactive_days)
        )

        filtered = []

        for deal in deals:

            last_updated = datetime.strptime(
                deal["last_updated"],
                "%Y-%m-%d"
            ).date()

            if last_updated < cutoff_date:

                filtered.append(deal)

        deals = filtered

    return deals


def get_deal_by_id(deal_id: str):

    data = load_data()

    for deal in data["deals"]:

        if deal["id"] == deal_id:

            return deal

    return None


# =========================================================
# LEAD TOOLS
# =========================================================

def count_leads_by_status(
    status: str
):

    data = load_data()

    normalized_status = status.strip().title()

    if normalized_status not in VALID_STATUSES:

        return {
            "success": False,
            "error": (
                f"Invalid status '{status}'. "
                f"Valid statuses are: "
                f"{', '.join(sorted(VALID_STATUSES))}"
            )
        }

    count = sum(
        1
        for deal in data["deals"]
        if deal["status"] == normalized_status
    )

    return {
        "success": True,
        "status": normalized_status,
        "count": count
    }


# =========================================================
# CUSTOMER HISTORY
# =========================================================

def get_customer_history(
    customer_id: str
):

    data = load_data()

    customer = get_customer_by_id(
        customer_id
    )

    if not customer:

        return {
            "success": False,
            "error": "Customer not found."
        }

    notes = [
        note
        for note in data["notes"]
        if note["customer_id"] == customer_id
    ]

    interactions = [
        interaction
        for interaction in data["interactions"]
        if interaction["customer_id"] == customer_id
    ]

    deals = [
        deal
        for deal in data["deals"]
        if deal["customer_id"] == customer_id
    ]

    return {
        "success": True,
        "customer": customer,
        "deals": deals,
        "notes": notes,
        "interactions": interactions
    }


# =========================================================
# WRITE TOOL: UPDATE DEAL STATUS
# =========================================================

def update_deal_status(
    deal_id: str,
    new_status: str
):

    data = load_data()

    normalized_status = (
        new_status.strip().title()
    )

    if normalized_status not in VALID_STATUSES:

        return {
            "success": False,
            "error": (
                f"Invalid status '{new_status}'."
            )
        }

    deal = None

    for item in data["deals"]:

        if item["id"] == deal_id:

            deal = item
            break

    if not deal:

        return {
            "success": False,
            "error": (
                f"Deal '{deal_id}' was not found."
            )
        }

    old_status = deal["status"]

    deal["status"] = normalized_status

    deal["last_updated"] = (
        datetime.now().strftime("%Y-%m-%d")
    )

    save_data(data)

    return {
        "success": True,
        "deal_id": deal_id,
        "old_status": old_status,
        "new_status": normalized_status
    }


# =========================================================
# WRITE TOOL: ADD NOTE
# =========================================================

def add_customer_note(
    customer_id: str,
    note_text: str,
    author: str = "AI CRM Assistant"
):

    data = load_data()

    customer = get_customer_by_id(
        customer_id
    )

    if not customer:

        return {
            "success": False,
            "error": "Customer not found."
        }

    if not note_text.strip():

        return {
            "success": False,
            "error": "Note cannot be empty."
        }

    existing_ids = [
        note["id"]
        for note in data["notes"]
    ]

    numeric_ids = []

    for note_id in existing_ids:

        try:
            numeric_ids.append(
                int(note_id.replace("N", ""))
            )
        except ValueError:
            pass

    next_id = (
        max(numeric_ids, default=0) + 1
    )

    new_note = {
        "id": f"N{next_id:03d}",
        "customer_id": customer_id,
        "text": note_text.strip(),
        "created_at": datetime.now().strftime(
            "%Y-%m-%d"
        ),
        "author": author
    }

    data["notes"].append(new_note)

    save_data(data)

    return {
        "success": True,
        "note": new_note,
        "customer": customer
    }


# =========================================================
# WRITE TOOL: ASSIGN LEAD
# =========================================================

def assign_lead(
    deal_id: str,
    salesperson: str
):

    data = load_data()

    deal = None

    for item in data["deals"]:

        if item["id"] == deal_id:

            deal = item
            break

    if not deal:

        return {
            "success": False,
            "error": "Deal/lead not found."
        }

    if not salesperson.strip():

        return {
            "success": False,
            "error": "Salesperson cannot be empty."
        }

    old_salesperson = deal["salesperson"]

    deal["salesperson"] = salesperson.strip()

    deal["last_updated"] = (
        datetime.now().strftime("%Y-%m-%d")
    )

    save_data(data)

    return {
        "success": True,
        "deal_id": deal_id,
        "old_salesperson": old_salesperson,
        "new_salesperson": salesperson.strip()
    }


# =========================================================
# SMART FEATURE: DEALS AT RISK
# =========================================================

def get_at_risk_deals(
    inactive_days: int = 14,
    min_value: float = 10000
):

    deals = search_deals(
        min_value=min_value,
        inactive_days=inactive_days
    )

    risky_deals = [
        deal
        for deal in deals
        if deal["status"] in {
            "New",
            "Contacted"
        }
    ]

    return risky_deals