"""OmniDebate Custom Widget Library."""

from omnidebate.ui.widgets.command_hud import CommandHUD
from omnidebate.ui.widgets.side_ribbon import SideRibbon
from omnidebate.ui.widgets.system_log import SystemLog
from omnidebate.ui.widgets.quick_notes import QuickNotes
from omnidebate.ui.widgets.sparkline import SparklineBar
from omnidebate.ui.widgets.gauge import GaugeBar
from omnidebate.ui.widgets.heatmap import HeatmapGrid

__all__ = [
    "CommandHUD",
    "SideRibbon",
    "SystemLog",
    "QuickNotes",
    "SparklineBar",
    "GaugeBar",
    "HeatmapGrid",
]
