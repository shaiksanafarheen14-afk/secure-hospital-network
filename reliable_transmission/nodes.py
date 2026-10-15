# =============================================================================
# nodes.py — Sender and Receiver Department Nodes
# =============================================================================
# This module defines the hospital departments that act as sender and receiver
# nodes in our network simulation. Dummy patient-related data (no real info)
# is used just to represent realistic hospital messages.
# =============================================================================

# Dummy patient data messages — these are fictional and for demo purposes only
DUMMY_MESSAGES = {
    "ER_to_ICU": [
        "PatientID:P001 Status:Stable BP:120/80 HR:72",
        "PatientID:P002 Status:Critical BP:90/60 HR:110",
        "PatientID:P003 Status:Improving Temp:98.6F",
    ],
    "Lab_to_Ward": [
        "PatientID:P004 TestResult:BloodSugar:Normal",
        "PatientID:P005 TestResult:HbA1c:6.5 Diagnosis:PreDiabetic",
        "PatientID:P006 TestResult:CBC:Normal WBC:7.2",
    ],
    "Pharmacy_to_ICU": [
        "PatientID:P007 Medication:Amoxicillin Dose:500mg",
        "PatientID:P008 Medication:Insulin Dose:10Units",
        "PatientID:P009 Medication:Paracetamol Dose:1g",
    ],
}


class DepartmentNode:
    """
    Represents a hospital department acting as either a sender or receiver.

    Attributes:
        name  (str): Department name (e.g., "Emergency Room")
        role  (str): Either "sender" or "receiver"
        inbox (list): Stores successfully received messages
    """

    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.inbox = []  # Received and verified messages go here

    def get_messages(self, channel_key: str) -> list:
        """
        Returns a list of dummy messages for the given communication channel.

        Args:
            channel_key (str): Key from DUMMY_MESSAGES dict (e.g. 'ER_to_ICU')

        Returns:
            list[str]: List of message strings
        """
        return DUMMY_MESSAGES.get(channel_key, ["No data available"])

    def receive(self, message: str):
        """
        Stores a successfully delivered message in the inbox.

        Args:
            message (str): The verified, decoded message string
        """
        self.inbox.append(message)

    def show_inbox(self):
        """Prints all messages received by this department."""
        print(f"\n  [INBOX]  {self.name} -- Received Messages:")
        if not self.inbox:
            print("      (No messages received)")
        else:
            for i, msg in enumerate(self.inbox, 1):
                print(f"      [{i}] {msg}")
