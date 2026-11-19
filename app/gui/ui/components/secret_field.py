from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtWidgets import QWidget

from app.gui.ui import icons
from app.gui.ui import styles


class SecretField(QLineEdit):
    """Password input with a trailing show / hide toggle."""

    def __init__(
        self,
        object_name: str,
        placeholder: str = "",
        *,
        revealable: bool = True,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.setObjectName(object_name)
        self.setPlaceholderText(placeholder)
        self.setEchoMode(QLineEdit.EchoMode.Password)

        self.visibility_action = None
        if revealable:
            self.visibility_action = self.addAction(
                icons.icon("eye", styles.theme().muted),
                QLineEdit.ActionPosition.TrailingPosition,
            )
            self.visibility_action.setCheckable(True)  # pyright: ignore[reportOptionalMemberAccess]
            self.visibility_action.toggled.connect(self.set_revealed)  # pyright: ignore[reportOptionalMemberAccess, reportUnknownMemberType]
            self.set_revealed(False)

    def is_revealed(self) -> bool:
        return self.echoMode() == QLineEdit.EchoMode.Normal

    def set_revealed(self, revealed: bool) -> None:
        self.setEchoMode(
            QLineEdit.EchoMode.Normal if revealed else QLineEdit.EchoMode.Password
        )
        action = self.visibility_action
        if action is None:
            return
        action.setIcon(
            icons.icon("eye_off" if revealed else "eye", styles.theme().muted)
        )
        label = "Hide secret" if revealed else "Show secret"
        action.setText(label)
        action.setToolTip(label)
