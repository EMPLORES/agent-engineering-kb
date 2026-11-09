
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

CHECKPOINT_FILE = BASE_DIR / "day23_checkpoint.json"
PAYMENT_LEDGER_FILE = BASE_DIR / "day23_payment_ledger.json"


class SimulatedInterruption(Exception):
    pass


class IdempotencyConflict(Exception):
    pass


class CheckpointStore:
    def load(self):
        if not CHECKPOINT_FILE.exists():
            return {"completed_steps": [], "results": {}}

        with open(CHECKPOINT_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    def save(self, state):
        with open(CHECKPOINT_FILE, "w", encoding="utf-8") as file:
            json.dump(state, file, indent=4, ensure_ascii=False)

        print("[Checkpoint] State saved.")


class PaymentGateway:
    def __init__(self):
        self.ledger = self._load_ledger()

    def _load_ledger(self):
        if not PAYMENT_LEDGER_FILE.exists():
            return {}

        with open(PAYMENT_LEDGER_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    def _save_ledger(self):
        with open(PAYMENT_LEDGER_FILE, "w", encoding="utf-8") as file:
            json.dump(self.ledger, file, indent=4, ensure_ascii=False)

    def charge(self, order_id, amount, idempotency_key):
        print(f"[Payment] Request received: {idempotency_key}")

        # Check whether this request has already been processed.
        if idempotency_key in self.ledger:
            previous = self.ledger[idempotency_key]

            # The same key must not represent different operations.
            if (
                previous["order_id"] != order_id
                or previous["amount"] != amount
            ):
                raise IdempotencyConflict(
                    "The same idempotency key was used "
                    "with different payment parameters."
                )

            print("[Payment] Duplicate request detected.")
            print("[Payment] Returning previous payment result.")

            return previous["result"]

        # Simulate an actual payment.
        result = {
            "payment_id": "PAY-001",
            "order_id": order_id,
            "amount": amount,
            "status": "success"
        }

        self.ledger[idempotency_key] = {
            "order_id": order_id,
            "amount": amount,
            "result": result
        }

        # Persist the payment record before returning.
        self._save_ledger()

        print("[Payment] Payment processed successfully.")

        return result

    def successful_payment_count(self):
        return len(self.ledger)


class Runtime:
    def __init__(self, payment_gateway, simulate_interruption=False):
        self.checkpoint_store = CheckpointStore()
        self.payment_gateway = payment_gateway
        self.simulate_interruption = simulate_interruption

    def run(self):
        state = self.checkpoint_store.load()

        print("\n[Runtime] Loaded checkpoint.")
        print("[Runtime] Completed steps:", state["completed_steps"])

        step_name = "charge_order"

        if step_name in state["completed_steps"]:
            print("[Runtime] Payment step already completed. Skipping.")
            return "completed"

        try:
            result = self.payment_gateway.charge(
                order_id="ORDER-001",
                amount=100,
                idempotency_key="ORDER-001-PAYMENT"
            )

            # Simulate a crash after payment succeeds,
            # but before the checkpoint is saved.
            if self.simulate_interruption:
                self.simulate_interruption = False

                print(
                    "[Runtime] Simulated interruption "
                    "after payment but before checkpoint."
                )

                raise SimulatedInterruption()

            state["results"][step_name] = result
            state["completed_steps"].append(step_name)

            self.checkpoint_store.save(state)

            print("[Runtime] Execution completed.")
            return "completed"

        except SimulatedInterruption:
            print("[Runtime] Execution interrupted.")
            return "interrupted"


def reset_demo_files():
    for file_path in [CHECKPOINT_FILE, PAYMENT_LEDGER_FILE]:
        if file_path.exists():
            file_path.unlink()


def main():
    # Reset previous demo data for reproducible results.
    reset_demo_files()

    payment_gateway = PaymentGateway()

    print("=" * 50)
    print("FIRST EXECUTION")
    print("=" * 50)

    runtime_1 = Runtime(
        payment_gateway,
        simulate_interruption=True
    )

    first_result = runtime_1.run()

    print("\nFirst execution result:", first_result)

    print("\n" + "=" * 50)
    print("SECOND EXECUTION")
    print("=" * 50)

    # Create a new Runtime to simulate a restart.
    runtime_2 = Runtime(payment_gateway)

    second_result = runtime_2.run()

    print("\nSecond execution result:", second_result)

    print("\n" + "=" * 50)
    print("FINAL RESULT")
    print("=" * 50)

    print(
        "Actual successful payments:",
        payment_gateway.successful_payment_count()
    )

    print("First execution:", first_result)
    print("Second execution:", second_result)


if __name__ == "__main__":
    main()
