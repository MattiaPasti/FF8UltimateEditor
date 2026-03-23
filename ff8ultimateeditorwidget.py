from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QCheckBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QSplitter,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from CCGroup.ccgroup import CCGroupWidget
from DrawEditor.draweditorwidget import DrawEditorWidget
from ExeLauncher.launcher import ProcessLauncher
from IfritAI.ifritaiwidget import IfritAIWidget
from IfritSeq.ifritseqwidget import IfritSeqWidget
from IfritTexture.ifrittexturewidget import IfritTextureWidget
from IfritXlsx.ifritxlsxwidget import IfritXlsxWidget
from ShumiTranslator.shumitranslator import ShumiTranslator
from TonberryShop.tonberryshop import TonberryShop
from ToolUpdate.toolupdatewidget import ToolUpdateWidget


@dataclass(frozen=True)
class ToolDefinition:
    tool_id: str
    name: str
    summary: str
    detail: str
    category: str
    kind: str
    keywords: tuple[str, ...]
    icon_name: str | None = None
    widget_factory: Callable[[], QWidget] | None = None
    launcher_path: str | None = None
    update_names: tuple[str, ...] = ()
    featured: bool = False

    @property
    def search_blob(self) -> str:
        return " ".join(
            (
                self.name,
                self.summary,
                self.detail,
                self.category,
                self.kind,
                *self.keywords,
            )
        ).lower()


class ToolCardButton(QPushButton):
    def __init__(self, title: str, summary: str, callback: Callable[[], None]):
        super().__init__(f"{title}\n{summary}")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("ToolCardButton")
        self.clicked.connect(callback)


class FF8UltimateEditorWidget(QWidget):
    HOME_ID = "home"

    def __init__(self, resources_path: str = "Resources", game_data_path: str = "FF8GameData"):
        super().__init__()

        if getattr(sys, "frozen", False):
            self.setup_logging()

        self.resources_path = Path(resources_path)
        self.game_data_path = Path(game_data_path)
        self._current_filter = "all"
        self._current_tool_id = self.HOME_ID
        self._tool_items: dict[str, QListWidgetItem] = {}
        self._tool_definitions = self._build_tool_definitions()
        self._tools_by_id = {tool.tool_id: tool for tool in self._tool_definitions}
        self._tool_page_indexes: dict[str, int] = {}
        self._launcher_by_tool_id = self._build_launchers()
        self._update_checkboxes: dict[str, QCheckBox] = {}

        self.setObjectName("UltimateRoot")
        self.setWindowTitle("FF8 Ultimate Editor")
        self.setWindowIcon(QIcon(str(self.resources_path / "hobbitdur.ico")))
        self.resize(1600, 980)
        self.setMinimumSize(1180, 760)

        self._build_interface()
        self._populate_tool_list()
        self._apply_styles()
        self._select_tool(self.HOME_ID)

    def _build_tool_definitions(self) -> list[ToolDefinition]:
        resources = str(self.resources_path)
        game_data = str(self.game_data_path)

        return [
            ToolDefinition(
                tool_id="ifrit_ai",
                name="IfritAI",
                summary="Monster AI editor",
                detail="Open, inspect and recompile battle AI scripts with the integrated Python editor.",
                category="Battle",
                kind="internal",
                keywords=("monster", "battle", "script", "ai", "ifrit"),
                icon_name="hobbitdur.ico",
                widget_factory=lambda: IfritAIWidget(icon_path=resources, game_data_folder=game_data),
                featured=True,
            ),
            ToolDefinition(
                tool_id="ifrit_xlsx",
                name="IfritXlsx",
                summary="Monster stat editor",
                detail="Edit monster values and export balancing data with the XLSX-oriented workflow.",
                category="Battle",
                kind="internal",
                keywords=("monster", "stats", "xlsx", "export", "import"),
                icon_name="hobbitdur.ico",
                widget_factory=lambda: IfritXlsxWidget(icon_path=resources, game_data_folder=game_data),
                featured=True,
            ),
            ToolDefinition(
                tool_id="shumi_translator",
                name="ShumiTranslator",
                summary="Full text editor",
                detail="Manage field, world, menu and executable text with a single translation workspace.",
                category="Text",
                kind="internal",
                keywords=("text", "translation", "field", "world", "exe", "kernel"),
                icon_name="shumitranslator.ico",
                widget_factory=lambda: ShumiTranslator(icon_path=resources, game_data_folder=game_data),
                featured=True,
            ),
            ToolDefinition(
                tool_id="tonberry_shop",
                name="TonberryShop",
                summary="Shop data editor",
                detail="Inspect and edit shop inventories from the in-game store database.",
                category="Economy",
                kind="internal",
                keywords=("shop", "items", "economy", "store", "buy"),
                icon_name="tonberryshop.ico",
                widget_factory=lambda: TonberryShop(resource_folder=resources),
                featured=True,
            ),
            ToolDefinition(
                tool_id="cc_group",
                name="CCGroup",
                summary="Triple Triad card editor",
                detail="Adjust card rewards and values for the CC Group battles.",
                category="Cards",
                kind="internal",
                keywords=("card", "triple triad", "cc group", "reward"),
                icon_name="ccgroup.ico",
                widget_factory=lambda: CCGroupWidget(icon_path=resources, game_data_path=game_data),
            ),
            ToolDefinition(
                tool_id="ifrit_seq",
                name="IfritSeq",
                summary="Animation sequence editor",
                detail="Inspect animation sequences and related timing data for battle content.",
                category="Animation",
                kind="internal",
                keywords=("animation", "sequence", "battle", "effects"),
                icon_name="hobbitdur.ico",
                widget_factory=lambda: IfritSeqWidget(icon_path=resources, game_data_folder=game_data),
            ),
            ToolDefinition(
                tool_id="draw_editor",
                name="Draw Editor",
                summary="Draw point editor",
                detail="Tune draw data and related extraction values from the Python editor.",
                category="Magic",
                kind="internal",
                keywords=("draw", "magic", "points", "spell"),
                icon_name="hobbitdur.ico",
                widget_factory=lambda: DrawEditorWidget(icon_path=resources, game_data_folder=game_data),
            ),
            ToolDefinition(
                tool_id="ifrit_texture",
                name="IfritTexture",
                summary="Monster texture browser",
                detail="Inspect battle textures with the integrated texture analysis workflow.",
                category="Graphics",
                kind="internal",
                keywords=("texture", "graphics", "monster", "tim", "battle"),
                icon_name="hobbitdur.ico",
                widget_factory=lambda: IfritTextureWidget(game_data_folder=game_data),
            ),
            ToolDefinition(
                tool_id="self_updater",
                name="FF8 Ultimate Editor",
                summary="Packaged launcher and updater",
                detail="Launch the packaged executable build and include it in update batches when needed.",
                category="Maintenance",
                kind="external",
                keywords=("self", "update", "launcher", "packaged"),
                icon_name="hobbitdur.ico",
                launcher_path="FF8UltimateEditor.exe",
                update_names=("Self",),
            ),
            ToolDefinition(
                tool_id="ifrit_gui",
                name="Ifrit GUI",
                summary="Original stat editor",
                detail="Launch the original external editor for legacy monster stat workflows.",
                category="External",
                kind="external",
                keywords=("legacy", "monster", "stats", "external"),
                icon_name="ifritGui.ico",
                launcher_path=os.path.join("ExternalTools", "IfritGui", "Ifrit.exe"),
                update_names=("IfritGui",),
            ),
            ToolDefinition(
                tool_id="quezacotl",
                name="Quezacotl",
                summary="init.out editor",
                detail="Launch the external tool for new game and initial state data editing.",
                category="External",
                kind="external",
                keywords=("init.out", "new game", "external"),
                icon_name="quezacotl.ico",
                launcher_path=os.path.join("ExternalTools", "Quezacotl", "Quezacotl.exe"),
                update_names=("Quezacotl",),
            ),
            ToolDefinition(
                tool_id="siren",
                name="Siren",
                summary="price.bin editor",
                detail="Launch the dedicated external editor for price tables and economy tuning.",
                category="External",
                kind="external",
                keywords=("price", "price.bin", "economy", "external"),
                icon_name="siren.ico",
                launcher_path=os.path.join("ExternalTools", "Siren", "Siren.exe"),
                update_names=("Siren",),
            ),
            ToolDefinition(
                tool_id="junkshop",
                name="Junkshop",
                summary="mweapon.bin editor",
                detail="Launch the external editor for weapon and magazine related data.",
                category="External",
                kind="external",
                keywords=("weapon", "junkshop", "mweapon.bin", "external"),
                icon_name="junkshop.ico",
                launcher_path=os.path.join("ExternalTools", "Junkshop", "Junkshop.exe"),
                update_names=("Junkshop",),
            ),
            ToolDefinition(
                tool_id="doomtrain",
                name="Doomtrain",
                summary="kernel.bin editor",
                detail="Launch the classic kernel editor for deep gameplay and command data edits.",
                category="External",
                kind="external",
                keywords=("kernel", "kernel.bin", "abilities", "external"),
                icon_name="doomtrain.ico",
                launcher_path=os.path.join("ExternalTools", "Doomtrain", "Doomtrain.exe"),
                update_names=("Doomtrain",),
            ),
            ToolDefinition(
                tool_id="jumbo_cactuar",
                name="Jumbo Cactuar",
                summary="scene.out editor",
                detail="Launch the external scene editor for battle encounters and formations.",
                category="External",
                kind="external",
                keywords=("scene", "scene.out", "battle", "external"),
                icon_name="jumbo_cactuar.ico",
                launcher_path=os.path.join("ExternalTools", "JumboCactuar", "Jumbo Cactuar.exe"),
                update_names=("JumboCactuar",),
            ),
            ToolDefinition(
                tool_id="deling",
                name="Deling",
                summary="Archive editor",
                detail="Launch Deling and keep both the GUI and CLI components aligned from the updater.",
                category="External",
                kind="external",
                keywords=("archive", "field", "deling", "external"),
                icon_name="deling.ico",
                launcher_path=os.path.join("ExternalTools", "Deling", "Deling.exe"),
                update_names=("Deling", "DelingCli"),
            ),
            ToolDefinition(
                tool_id="hyne",
                name="Hyne",
                summary="Save editor",
                detail="Launch the external save editor for quick party, inventory and progression changes.",
                category="External",
                kind="external",
                keywords=("save", "hyne", "external"),
                icon_name="hyne.ico",
                launcher_path=os.path.join("ExternalTools", "Hyne", "Hyne.exe"),
                update_names=("Hyne",),
            ),
        ]

    def _build_launchers(self) -> dict[str, ProcessLauncher]:
        launchers: dict[str, ProcessLauncher] = {}
        for tool in self._tool_definitions:
            if tool.launcher_path:
                launchers[tool.tool_id] = ProcessLauncher(tool.launcher_path)
        return launchers

    def _resource_icon(self, icon_name: str | None, fallback: str = "icon.ico") -> QIcon:
        candidates = []
        if icon_name:
            candidates.append(self.resources_path / icon_name)
        if fallback:
            candidates.append(self.resources_path / fallback)

        for candidate in candidates:
            if candidate.exists():
                return QIcon(str(candidate))
        return QIcon()

    def _tool_icon(self, tool: ToolDefinition) -> QIcon:
        return self._resource_icon(tool.icon_name)

    def _build_interface(self) -> None:
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(18)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        main_layout.addWidget(splitter)

        sidebar = QFrame()
        sidebar.setObjectName("SidebarPanel")
        sidebar.setMinimumWidth(340)
        sidebar.setMaximumWidth(420)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(22, 22, 22, 22)
        sidebar_layout.setSpacing(16)
        sidebar_layout.addWidget(self._build_brand_card())

        self._search_input = QLineEdit()
        self._search_input.setObjectName("SearchInput")
        self._search_input.setPlaceholderText("Search tools, files or keywords")
        self._search_input.textChanged.connect(self._apply_filters)
        sidebar_layout.addWidget(self._search_input)

        sidebar_layout.addLayout(self._build_filter_row())

        self._tool_list = QListWidget()
        self._tool_list.setObjectName("ToolList")
        self._tool_list.setIconSize(QSize(18, 18))
        self._tool_list.setWordWrap(True)
        self._tool_list.setTextElideMode(Qt.TextElideMode.ElideNone)
        self._tool_list.setMinimumHeight(150)
        self._tool_list.currentItemChanged.connect(self._on_tool_changed)
        sidebar_layout.addWidget(self._tool_list, stretch=1)

        sidebar_layout.addWidget(self._build_update_center())
        sidebar_layout.addWidget(self._build_workspace_card())

        content = QFrame()
        content.setObjectName("ContentShell")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(18)

        header = QFrame()
        header.setObjectName("HeaderCard")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(24, 24, 24, 24)
        header_layout.setSpacing(12)

        meta_row = QHBoxLayout()
        meta_row.setSpacing(10)
        self._tool_kind_label = QLabel()
        self._tool_kind_label.setObjectName("KindLabel")
        self._tool_category_label = QLabel()
        self._tool_category_label.setObjectName("CategoryLabel")
        meta_row.addWidget(self._tool_kind_label)
        meta_row.addWidget(self._tool_category_label)
        meta_row.addStretch(1)
        header_layout.addLayout(meta_row)

        self._tool_title_label = QLabel()
        self._tool_title_label.setObjectName("ToolTitleLabel")
        header_layout.addWidget(self._tool_title_label)

        self._tool_summary_label = QLabel()
        self._tool_summary_label.setObjectName("ToolSummaryLabel")
        self._tool_summary_label.setWordWrap(True)
        header_layout.addWidget(self._tool_summary_label)

        self._tool_meta_label = QLabel()
        self._tool_meta_label.setObjectName("ToolMetaLabel")
        self._tool_meta_label.setWordWrap(True)
        header_layout.addWidget(self._tool_meta_label)

        action_row = QHBoxLayout()
        action_row.setSpacing(10)
        self._primary_action_button = QPushButton()
        self._primary_action_button.setObjectName("PrimaryActionButton")
        self._primary_action_button.clicked.connect(self._handle_primary_action)
        self._secondary_action_button = QPushButton()
        self._secondary_action_button.setObjectName("SecondaryActionButton")
        self._secondary_action_button.clicked.connect(self._toggle_current_update_selection)
        action_row.addWidget(self._primary_action_button)
        action_row.addWidget(self._secondary_action_button)
        action_row.addStretch(1)
        header_layout.addLayout(action_row)
        content_layout.addWidget(header)

        self._content_stack = QStackedWidget()
        self._content_stack.setObjectName("ContentStack")
        self._home_page = self._build_home_page()
        self._external_page = self._build_external_page()
        self._content_stack.addWidget(self._home_page)
        self._content_stack.addWidget(self._external_page)
        content_layout.addWidget(self._content_stack, stretch=1)

        splitter.addWidget(sidebar)
        splitter.addWidget(content)
        splitter.setSizes([360, 1240])

    def _build_brand_card(self) -> QWidget:
        card = QFrame()
        card.setObjectName("BrandCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(8)

        eyebrow = QLabel("Python Modding Hub")
        eyebrow.setObjectName("EyebrowLabel")
        layout.addWidget(eyebrow)

        title = QLabel("FF8 Ultimate Editor")
        title.setObjectName("BrandTitleLabel")
        layout.addWidget(title)

        subtitle = QLabel(
            "One modern workspace for the built-in editors, the legacy utilities and the updater flow."
        )
        subtitle.setWordWrap(True)
        subtitle.setObjectName("BrandSubtitleLabel")
        layout.addWidget(subtitle)

        stats = QLabel(
            f"{len(self._internal_tools())} integrated editors | {len(self._external_tools())} external launchers"
        )
        stats.setObjectName("BrandStatsLabel")
        layout.addWidget(stats)
        return card

    def _build_filter_row(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(8)

        self._filter_group = QButtonGroup(self)
        self._filter_group.setExclusive(True)

        for label, value in (("All", "all"), ("Editors", "internal"), ("Launchers", "external")):
            button = QPushButton(label)
            button.setObjectName("FilterButton")
            button.setCheckable(True)
            button.clicked.connect(lambda checked, current=value: self._set_filter(current))
            if value == "all":
                button.setChecked(True)
            self._filter_group.addButton(button)
            layout.addWidget(button)

        return layout

    def _build_update_center(self) -> QWidget:
        card = QFrame()
        card.setObjectName("SidebarCard")
        card.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title = QLabel("Update Center")
        title.setObjectName("SidebarCardTitle")
        layout.addWidget(title)

        subtitle = QLabel("Choose what to keep aligned, then launch the updater without leaving the hub.")
        subtitle.setWordWrap(True)
        subtitle.setObjectName("SidebarCardBody")
        layout.addWidget(subtitle)

        checkbox_scroll = QScrollArea()
        checkbox_scroll.setWidgetResizable(True)
        checkbox_scroll.setFrameShape(QFrame.Shape.NoFrame)
        checkbox_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        checkbox_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        checkbox_scroll.setMaximumHeight(176)

        checkbox_holder = QWidget()
        checkbox_layout = QVBoxLayout(checkbox_holder)
        checkbox_layout.setContentsMargins(0, 0, 4, 0)
        checkbox_layout.setSpacing(8)

        for tool in [self._tools_by_id["self_updater"], *self._external_tools()]:
            checkbox = QCheckBox(tool.name)
            checkbox.setIcon(self._tool_icon(tool))
            checkbox.setIconSize(QSize(16, 16))
            checkbox.toggled.connect(
                lambda checked, tool_id=tool.tool_id: self._sync_update_checkbox(tool_id, checked)
            )
            self._update_checkboxes[tool.tool_id] = checkbox
            checkbox_layout.addWidget(checkbox)

        checkbox_layout.addStretch(1)
        checkbox_scroll.setWidget(checkbox_holder)
        layout.addWidget(checkbox_scroll)

        self._tool_update_widget = ToolUpdateWidget(self.tools_to_update, resource_path=str(self.resources_path))
        self._tool_update_widget.setObjectName("UpdaterWidget")
        self._tool_update_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self._tool_update_widget.download_button_widget.setObjectName("UpdateDownloadButton")
        self._tool_update_widget.canal_widget.setObjectName("UpdateChannelBox")
        self._tool_update_widget.progress.setObjectName("UpdateProgressBar")
        self._tool_update_widget.progress_current_download.setObjectName("UpdateProgressBar")
        layout.addWidget(self._tool_update_widget)
        return card

    def _build_workspace_card(self) -> QWidget:
        card = QFrame()
        card.setObjectName("SidebarCard")
        card.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(8)

        title = QLabel("Workspace")
        title.setObjectName("SidebarCardTitle")
        layout.addWidget(title)

        body = QLabel(
            f"Resources: {self.resources_path}\nGame data: {self.game_data_path}\nLazy loading keeps startup lighter and the shell easier to extend."
        )
        body.setWordWrap(True)
        body.setObjectName("SidebarCardBody")
        layout.addWidget(body)
        return card

    def _build_home_page(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        body = QWidget()
        layout = QVBoxLayout(body)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)

        intro = QFrame()
        intro.setObjectName("HomeIntroCard")
        intro_layout = QVBoxLayout(intro)
        intro_layout.setContentsMargins(24, 24, 24, 24)
        intro_layout.setSpacing(10)
        intro_title = QLabel("Choose a tool and keep the workspace focused.")
        intro_title.setObjectName("HomeIntroTitle")
        intro_layout.addWidget(intro_title)
        intro_body = QLabel(
            "The shell now groups editors, launchers and updates in one place. Internal modules open on demand, external tools stay reachable, and future additions only need a new tool definition."
        )
        intro_body.setWordWrap(True)
        intro_body.setObjectName("HomeIntroBody")
        intro_layout.addWidget(intro_body)
        layout.addWidget(intro)

        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(12)
        metrics_layout.addWidget(self._build_metric_card("Editors", str(len(self._internal_tools()))))
        metrics_layout.addWidget(self._build_metric_card("Launchers", str(len(self._external_tools()))))
        metrics_layout.addWidget(self._build_metric_card("Update Targets", str(len(self._update_checkboxes))))
        layout.addLayout(metrics_layout)

        layout.addWidget(
            self._build_tool_section(
                "Featured editors",
                [tool for tool in self._internal_tools() if tool.featured],
            )
        )
        layout.addWidget(self._build_tool_section("All built-in editors", self._internal_tools()))
        layout.addWidget(self._build_tool_section("Legacy launchers", self._external_tools()))
        layout.addStretch(1)

        scroll.setWidget(body)
        return scroll

    def _build_metric_card(self, label: str, value: str) -> QWidget:
        card = QFrame()
        card.setObjectName("MetricCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(4)
        value_label = QLabel(value)
        value_label.setObjectName("MetricValueLabel")
        layout.addWidget(value_label)
        text_label = QLabel(label)
        text_label.setObjectName("MetricTextLabel")
        layout.addWidget(text_label)
        return card

    def _build_tool_section(self, title: str, tools: list[ToolDefinition]) -> QWidget:
        section = QFrame()
        section.setObjectName("SectionCard")
        layout = QVBoxLayout(section)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        heading = QLabel(title)
        heading.setObjectName("SectionTitleLabel")
        layout.addWidget(heading)

        grid = QGridLayout()
        grid.setSpacing(12)
        for index, tool in enumerate(tools):
            button = ToolCardButton(
                tool.name,
                tool.summary,
                lambda checked=False, tool_id=tool.tool_id: self._select_tool(tool_id),
            )
            grid.addWidget(button, index // 2, index % 2)
        layout.addLayout(grid)
        return section

    def _build_external_page(self) -> QWidget:
        page = QFrame()
        page.setObjectName("LaunchPage")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)

        status_card = QFrame()
        status_card.setObjectName("SectionCard")
        status_layout = QVBoxLayout(status_card)
        status_layout.setContentsMargins(20, 20, 20, 20)
        status_layout.setSpacing(10)

        self._external_status_label = QLabel()
        self._external_status_label.setObjectName("SectionTitleLabel")
        status_layout.addWidget(self._external_status_label)

        self._external_path_label = QLabel()
        self._external_path_label.setWordWrap(True)
        self._external_path_label.setObjectName("SidebarCardBody")
        status_layout.addWidget(self._external_path_label)

        self._external_update_label = QLabel()
        self._external_update_label.setWordWrap(True)
        self._external_update_label.setObjectName("SidebarCardBody")
        status_layout.addWidget(self._external_update_label)

        self._external_launch_button = QPushButton("Launch external tool")
        self._external_launch_button.setObjectName("PrimaryActionButton")
        self._external_launch_button.clicked.connect(self._launch_current_tool)
        status_layout.addWidget(self._external_launch_button, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(status_card)

        note_card = QFrame()
        note_card.setObjectName("SectionCard")
        note_layout = QVBoxLayout(note_card)
        note_layout.setContentsMargins(20, 20, 20, 20)
        note_layout.setSpacing(10)

        note_title = QLabel("Integration note")
        note_title.setObjectName("SectionTitleLabel")
        note_layout.addWidget(note_title)

        self._external_note_label = QLabel(
            "External utilities are still supported through Python launchers so the shell can stay unified while each legacy tool is modernized separately."
        )
        self._external_note_label.setWordWrap(True)
        self._external_note_label.setObjectName("SidebarCardBody")
        note_layout.addWidget(self._external_note_label)
        layout.addWidget(note_card)
        layout.addStretch(1)
        return page

    def _populate_tool_list(self) -> None:
        home_item = QListWidgetItem("Overview\nDashboard and quick actions")
        home_item.setIcon(self._resource_icon("info.png"))
        home_item.setData(Qt.ItemDataRole.UserRole, self.HOME_ID)
        home_item.setData(Qt.ItemDataRole.UserRole + 1, "overview dashboard home")
        home_item.setSizeHint(QSize(0, 84))
        self._tool_list.addItem(home_item)
        self._tool_items[self.HOME_ID] = home_item

        for tool in self._tool_definitions:
            item = QListWidgetItem(f"{tool.name}\n{tool.summary}")
            item.setIcon(self._tool_icon(tool))
            item.setData(Qt.ItemDataRole.UserRole, tool.tool_id)
            item.setData(Qt.ItemDataRole.UserRole + 1, tool.search_blob)
            item.setToolTip(tool.detail)
            item.setSizeHint(QSize(0, 84))
            self._tool_list.addItem(item)
            self._tool_items[tool.tool_id] = item

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            """
            QWidget#UltimateRoot {
                background-color: qradialgradient(
                    cx: 0.18, cy: 0.14, radius: 1.15,
                    fx: 0.18, fy: 0.14,
                    stop: 0 #18364a,
                    stop: 0.25 #0d1826,
                    stop: 0.62 #09111d,
                    stop: 1 #050a12
                );
                color: #eff7ff;
                font-family: "Segoe UI Variable Display", "Bahnschrift", "Segoe UI";
            }
            QFrame#SidebarPanel,
            QFrame#SidebarCard,
            QFrame#MetricCard,
            QFrame#SectionCard,
            QFrame#HomeIntroCard,
            QFrame#LaunchPage {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #101926,
                    stop: 0.55 #0c1420,
                    stop: 1 #09101a
                );
                border: 1px solid #1f3148;
                border-radius: 24px;
            }
            QFrame#BrandCard {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #13253a,
                    stop: 0.46 #102035,
                    stop: 1 #17213f
                );
                border: 1px solid #2f4869;
                border-radius: 28px;
            }
            QFrame#HeaderCard {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #0f1727,
                    stop: 0.5 #101a2b,
                    stop: 1 #0c1323
                );
                border: 1px solid #2b405f;
                border-radius: 28px;
            }
            QFrame#ContentShell {
                background: transparent;
            }
            QFrame#SidebarPanel:hover,
            QFrame#SidebarCard:hover,
            QFrame#MetricCard:hover,
            QFrame#SectionCard:hover,
            QFrame#HomeIntroCard:hover,
            QFrame#HeaderCard:hover,
            QFrame#BrandCard:hover {
                border-color: #38557b;
            }
            QSplitter::handle {
                background: #0a111b;
                width: 10px;
                margin: 10px 0;
                border-radius: 4px;
            }
            QLabel#EyebrowLabel {
                color: #64f0d6;
                font-size: 11px;
                font-weight: 700;
            }
            QLabel#BrandTitleLabel, QLabel#ToolTitleLabel, QLabel#HomeIntroTitle {
                color: #f5fbff;
                font-size: 30px;
                font-weight: 700;
            }
            QLabel#BrandSubtitleLabel, QLabel#ToolSummaryLabel, QLabel#HomeIntroBody, QLabel#SidebarCardBody {
                color: #94a8c3;
                font-size: 14px;
            }
            QLabel#BrandStatsLabel, QLabel#ToolMetaLabel, QLabel#MetricTextLabel {
                color: #7b91ad;
                font-size: 12px;
                font-weight: 600;
            }
            QLabel#KindLabel, QLabel#CategoryLabel {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #122d34, stop: 1 #173f42);
                color: #7af7df;
                border: 1px solid #245f67;
                border-radius: 13px;
                padding: 6px 12px;
                font-size: 11px;
                font-weight: 700;
            }
            QLabel#CategoryLabel {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #2c2913, stop: 1 #3a3210);
                color: #f5d26a;
                border: 1px solid #6b5a1a;
            }
            QLineEdit#SearchInput {
                background: #0a1320;
                border: 1px solid #22354d;
                border-radius: 18px;
                padding: 13px 16px;
                font-size: 14px;
                color: #f5fbff;
                selection-background-color: #57f0d8;
                selection-color: #041018;
            }
            QLineEdit#SearchInput:focus {
                border: 1px solid #57f0d8;
                background: #0d1828;
            }
            QPushButton#FilterButton, QPushButton#SecondaryActionButton {
                background: #0c1523;
                border: 1px solid #223754;
                border-radius: 16px;
                padding: 10px 14px;
                font-size: 13px;
                font-weight: 700;
                color: #dbe8f9;
            }
            QPushButton#FilterButton:hover, QPushButton#SecondaryActionButton:hover {
                border-color: #57f0d8;
                color: #ffffff;
                background: #122133;
            }
            QPushButton#FilterButton:checked {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #35cbd6, stop: 1 #61f0b8);
                border-color: #7cf4d1;
                color: #041018;
            }
            QPushButton#PrimaryActionButton, QPushButton#UpdateDownloadButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #27d1d8, stop: 1 #76f38b);
                border: 1px solid #90f6bb;
                border-radius: 18px;
                padding: 12px 18px;
                color: #041018;
                font-size: 13px;
                font-weight: 800;
            }
            QPushButton#PrimaryActionButton:hover, QPushButton#UpdateDownloadButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #56e7ea, stop: 1 #9bff9c);
            }
            QPushButton#PrimaryActionButton:disabled {
                background: #122132;
                border-color: #1f3148;
                color: #59708b;
            }
            QPushButton#ToolCardButton {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #10192a,
                    stop: 1 #0b1220
                );
                border: 1px solid #243957;
                border-radius: 22px;
                padding: 18px;
                min-height: 84px;
                text-align: left;
                color: #eef6ff;
                font-size: 14px;
                font-weight: 700;
            }
            QPushButton#ToolCardButton:hover {
                border-color: #57f0d8;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #15243a,
                    stop: 1 #0f1730
                );
            }
            QListWidget#ToolList {
                background: transparent;
                border: none;
                outline: 0;
            }
            QListWidget#ToolList::item {
                background: #0c1522;
                border: 1px solid #1f3148;
                border-radius: 18px;
                padding: 15px;
                margin: 5px 0;
                color: #dce9fa;
            }
            QListWidget#ToolList::item:hover {
                border-color: #57f0d8;
                background: #132131;
            }
            QListWidget#ToolList::item:selected {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #1ac9d8, stop: 1 #58f0c1);
                border-color: #96ffe1;
                color: #021017;
            }
            QLabel#SidebarCardTitle, QLabel#SectionTitleLabel {
                color: #f5fbff;
                font-size: 18px;
                font-weight: 700;
            }
            QLabel#MetricValueLabel {
                color: #7cf4d1;
                font-size: 34px;
                font-weight: 800;
            }
            QCheckBox {
                color: #d9e7f9;
                spacing: 10px;
                font-size: 13px;
                font-weight: 600;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 6px;
                border: 1px solid #2b4261;
                background: #09121d;
            }
            QCheckBox::indicator:checked {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #24d5db, stop: 1 #7ef38e);
                border-color: #8df6c8;
            }
            QProgressBar#UpdateProgressBar {
                border: 1px solid #243754;
                border-radius: 11px;
                background: #08111c;
                text-align: center;
                min-height: 20px;
                color: #edf7ff;
            }
            QProgressBar#UpdateProgressBar::chunk {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #1ccad9, stop: 1 #79f18f);
                border-radius: 9px;
            }
            QComboBox#UpdateChannelBox {
                background: #0a1320;
                border: 1px solid #22354d;
                border-radius: 14px;
                padding: 8px 10px;
                color: #f5fbff;
                selection-background-color: #27d1d8;
                selection-color: #041018;
            }
            QComboBox#UpdateChannelBox:hover {
                border-color: #57f0d8;
            }
            QToolTip {
                background: #0f1828;
                color: #eff7ff;
                border: 1px solid #38557b;
                padding: 8px 10px;
            }
            QScrollBar:vertical {
                background: #09111b;
                width: 12px;
                margin: 6px 0 6px 0;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #223956;
                min-height: 34px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: #57f0d8;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: transparent;
                height: 0px;
            }
            """
        )

    def _set_filter(self, value: str) -> None:
        self._current_filter = value
        self._apply_filters()

    def _apply_filters(self) -> None:
        query = self._search_input.text().strip().lower()
        first_visible: QListWidgetItem | None = None

        for index in range(self._tool_list.count()):
            item = self._tool_list.item(index)
            tool_id = item.data(Qt.ItemDataRole.UserRole)

            if tool_id == self.HOME_ID:
                matches_query = not query or query in item.data(Qt.ItemDataRole.UserRole + 1)
                hidden = not matches_query
            else:
                tool = self._tools_by_id[tool_id]
                matches_kind = self._current_filter == "all" or tool.kind == self._current_filter
                matches_query = not query or query in tool.search_blob
                hidden = not (matches_kind and matches_query)

            item.setHidden(hidden)
            if not hidden and first_visible is None:
                first_visible = item

        current_item = self._tool_list.currentItem()
        if current_item is None or current_item.isHidden():
            if first_visible is not None:
                self._tool_list.setCurrentItem(first_visible)

    def _on_tool_changed(self, current: QListWidgetItem | None, previous: QListWidgetItem | None) -> None:
        del previous
        if current is None:
            return
        tool_id = current.data(Qt.ItemDataRole.UserRole)
        self._select_tool(tool_id)

    def _select_tool(self, tool_id: str) -> None:
        if tool_id not in self._tool_items:
            return

        item = self._tool_items[tool_id]
        if self._tool_list.currentItem() is not item:
            self._tool_list.setCurrentItem(item)
            return

        self._current_tool_id = tool_id

        if tool_id == self.HOME_ID:
            self._content_stack.setCurrentWidget(self._home_page)
            self._tool_kind_label.setText("Workspace")
            self._tool_category_label.setText("Overview")
            self._tool_title_label.setText("Modern FF8 workbench")
            self._tool_summary_label.setText(
                "Browse every editor from one Python shell, open heavy modules only when you need them, and keep the updater close at hand."
            )
            self._tool_meta_label.setText(
                f"Resources folder: {self.resources_path} | Game data folder: {self.game_data_path}"
            )
            self._primary_action_button.setText("Open IfritAI")
            self._primary_action_button.setEnabled(True)
            self._primary_action_button.show()
            self._secondary_action_button.hide()
            return

        tool = self._tools_by_id[tool_id]
        self._tool_kind_label.setText("Integrated editor" if tool.kind == "internal" else "External launcher")
        self._tool_category_label.setText(tool.category)
        self._tool_title_label.setText(tool.name)
        self._tool_summary_label.setText(tool.detail)
        self._tool_meta_label.setText(
            "Keywords: " + ", ".join(tool.keywords[:4]) + ("..." if len(tool.keywords) > 4 else "")
        )

        if tool.kind == "internal":
            widget = self._ensure_internal_tool_widget(tool)
            self._content_stack.setCurrentWidget(widget)
            self._primary_action_button.setEnabled(True)
            self._primary_action_button.hide()
            self._secondary_action_button.hide()
            return

        self._update_external_page(tool)
        self._content_stack.setCurrentWidget(self._external_page)
        self._primary_action_button.setText("Launch tool")
        self._primary_action_button.setEnabled(Path(tool.launcher_path or "").exists())
        self._primary_action_button.show()
        if tool.update_names:
            is_selected = self._update_checkboxes[tool.tool_id].isChecked()
            self._secondary_action_button.setText(
                "Included in updates" if is_selected else "Include in updates"
            )
            self._secondary_action_button.show()
        else:
            self._secondary_action_button.hide()

    def _ensure_internal_tool_widget(self, tool: ToolDefinition) -> QWidget:
        if tool.tool_id in self._tool_page_indexes:
            return self._content_stack.widget(self._tool_page_indexes[tool.tool_id])

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            widget = tool.widget_factory()
            index = self._content_stack.addWidget(widget)
            self._tool_page_indexes[tool.tool_id] = index
            return widget
        finally:
            QApplication.restoreOverrideCursor()

    def _update_external_page(self, tool: ToolDefinition) -> None:
        executable_path = Path(tool.launcher_path or "")
        exists = executable_path.exists()
        self._external_status_label.setText("Executable ready" if exists else "Executable not found")
        self._external_path_label.setText(f"Expected path: {executable_path}")
        update_targets = ", ".join(tool.update_names) if tool.update_names else "No updater target configured"
        self._external_update_label.setText(f"Update packages: {update_targets}")
        self._external_launch_button.setEnabled(exists)
        self._external_launch_button.setText("Launch external tool" if exists else "Tool not installed in this folder")

    def _handle_primary_action(self) -> None:
        if self._current_tool_id == self.HOME_ID:
            self._select_tool("ifrit_ai")
            return
        self._launch_current_tool()

    def _launch_current_tool(self) -> None:
        launcher = self._launcher_by_tool_id.get(self._current_tool_id)
        if launcher:
            launcher.launch()

    def _toggle_current_update_selection(self) -> None:
        if self._current_tool_id not in self._update_checkboxes:
            return
        checkbox = self._update_checkboxes[self._current_tool_id]
        checkbox.setChecked(not checkbox.isChecked())

    def _sync_update_checkbox(self, tool_id: str, checked: bool) -> None:
        if tool_id == self._current_tool_id:
            self._secondary_action_button.setText("Included in updates" if checked else "Include in updates")

    def tools_to_update(self) -> list[str]:
        selected: list[str] = []
        for tool_id, checkbox in self._update_checkboxes.items():
            if not checkbox.isChecked():
                continue
            for update_name in self._tools_by_id[tool_id].update_names:
                if update_name not in selected:
                    selected.append(update_name)

        if selected and "Self" not in selected and "VincentTim" not in selected:
            selected.append("VincentTim")
        return selected

    def _internal_tools(self) -> list[ToolDefinition]:
        return [tool for tool in self._tool_definitions if tool.kind == "internal"]

    def _external_tools(self) -> list[ToolDefinition]:
        return [tool for tool in self._tool_definitions if tool.kind == "external" and tool.tool_id != "self_updater"]

    @staticmethod
    def setup_logging() -> None:
        os.makedirs("logs", exist_ok=True)
        log_file = f"logs/FF8UltimateEditor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        sys.stdout = open(log_file, "w")
        sys.stderr = sys.stdout
