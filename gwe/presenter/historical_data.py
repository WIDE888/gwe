# This file is part of gwe.
#
# Copyright (c) 2018 Roberto Leinardi
#
# gsi is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# gsi is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with gsi.  If not, see <http://www.gnu.org/licenses/>.
import logging
from enum import Enum
from typing import Any, Tuple, Dict, Optional

from gi.repository import Gtk, GLib
from injector import singleton, inject

from gwe.model import Status, GpuStatus
from gwe.repository import NOT_AVAILABLE_STRING
from gwe.util.view import hide_on_delete

LOG = logging.getLogger(__name__)

MONITORING_INTERVAL = 300


class GraphType(Enum):
    GPU_CLOCK = 1
    MEMORY_CLOCK = 2
    GPU_TEMP = 3
    FAN_DUTY = 4
    FAN_RPM = 5
    GPU_LOAD = 6
    MEMORY_LOAD = 7
    MEMORY_USAGE = 8
    POWER_DRAW = 9


class HistoricalDataViewInterface:
    def show(self) -> None:
        raise NotImplementedError()

    def hide(self) -> None:
        raise NotImplementedError()

    def refresh_graphs(self, data: Dict[GraphType, Tuple[int, float, str, float, float]]) -> None:
        raise NotImplementedError()


@singleton
class HistoricalDataPresenter:
    @inject
    def __init__(self) -> None:
        LOG.debug("init HistoricalDataPresenter ")
        self.view: HistoricalDataViewInterface = HistoricalDataViewInterface()

    def add_status(self, new_status: Status) -> None:
        gpu_index = 0
        data: Dict[GraphType, Tuple[int, float, str, float, float]] = {}
        time = GLib.get_monotonic_time()
        gpu_status = new_status.gpu_status_list[gpu_index]
        gpu_clock = gpu_status.clocks.graphic_current
        if gpu_clock is not None:
            data[GraphType.GPU_CLOCK] = (time, float(gpu_clock), 'MHz', 0.0, 2000.0)
        mem_clock = gpu_status.clocks.memory_current
        if mem_clock is not None:
            data[GraphType.MEMORY_CLOCK] = (time, float(mem_clock), 'MHz', 0.0, 7000.0)
        gpu_temp = gpu_status.temp.gpu
        if gpu_temp is not None:
            data[GraphType.GPU_TEMP] = (time, float(gpu_temp), '°C', 0.0, 100.0)
        # fan_duty = gpu_status.fan.fan_list[0][0]
        # if fan_duty is not None:
        #     data[GraphType.FAN_DUTY] = (time, fan_duty, '%', 0.0, 100.0)
        # fan_rpm = gpu_status.
        # if fan_rpm is not None:
        #     data[GraphType.FAN_RPM] = (time, fan_rpm, 'rpm', 0.0, 2200.0)
        gpu_load = gpu_status.info.gpu_usage
        if gpu_load is not None:
            data[GraphType.GPU_LOAD] = (time, float(gpu_load), '%', 0.0, 100.0)
        mem_load = gpu_status.info.memory_usage
        if mem_load is not None:
            data[GraphType.MEMORY_LOAD] = (time, float(mem_load), '%', 0.0, 100.0)
        mem_usage = gpu_status.info.memory_used
        if mem_usage is not None:
            data[GraphType.MEMORY_USAGE] = (time, float(mem_usage), 'MiB', 0.0, float(gpu_status.info.memory_total))
        power_draw = gpu_status.power.draw
        if power_draw is not None:
            data[GraphType.POWER_DRAW] = (time, power_draw, 'W', 0.0, gpu_status.power.maximum)
        self.view.refresh_graphs(data)

    # @staticmethod
    # def _get_gpu_clock_data(gpu_status: GpuStatus) -> Optional[float]:
    #     if NOT_AVAILABLE_STRING not in gpu_status.clocks.graphic_current:
    #         return float(gpu_status.clocks.graphic_current.rstrip(' MHz'))
    #     return None
    #
    # @staticmethod
    # def _get_mem_clock_data(gpu_status: GpuStatus) -> Optional[float]:
    #     if NOT_AVAILABLE_STRING not in gpu_status.clocks.graphic_current:
    #         return float(gpu_status.clocks.memory_current.rstrip(' MHz'))
    #     return None
    #
    # @staticmethod
    # def _get_gpu_temp_data(gpu_status: GpuStatus) -> Optional[float]:
    #     if NOT_AVAILABLE_STRING not in gpu_status.temp.gpu:
    #         return float(gpu_status.temp.gpu.rstrip(' C'))
    #     return None
    #
    # @staticmethod
    # def _get_fan_duty_data(gpu_status: GpuStatus) -> Optional[float]:
    #     if gpu_status.fan.fan_list:
    #         return float(gpu_status.fan.fan_list[0][0])
    #     return None
    #
    # @staticmethod
    # def _get_fan_rpm_data(gpu_status: GpuStatus) -> Optional[float]:
    #     if gpu_status.fan.fan_list:
    #         return float(gpu_status.fan.fan_list[0][1])
    #     return None
    #
    # @staticmethod
    # def _get_gpu_load_data(gpu_status: GpuStatus) -> Optional[float]:
    #     if NOT_AVAILABLE_STRING not in gpu_status.info.gpu_usage:
    #         return float(gpu_status.info.gpu_usage.rstrip(' %'))
    #     return None
    #
    # @staticmethod
    # def _get_mem_load_data(gpu_status: GpuStatus) -> Optional[float]:
    #     if NOT_AVAILABLE_STRING not in gpu_status.info.memory_usage:
    #         return float(gpu_status.info.memory_usage.rstrip(' %'))
    #     return None
    #
    # @staticmethod
    # def _get_mem_usage_data(gpu_status: GpuStatus) -> Optional[Tuple[float, float]]:
    #     if NOT_AVAILABLE_STRING not in gpu_status.info.memory_size:
    #         mem_list = gpu_status.info.memory_size.split(' / ')
    #         return float(mem_list[0].rstrip(' MiB')), float(mem_list[1].rstrip(' MiB'))
    #     return None
    #
    # @staticmethod
    # def _get_power_draw_data(gpu_status: GpuStatus) -> Optional[float]:
    #     if NOT_AVAILABLE_STRING not in gpu_status.power.draw:
    #         return float(gpu_status.power.draw.rstrip(' W'))
    #     return None

    def show(self) -> None:
        self.view.show()

    def on_dialog_delete_event(self, widget: Gtk.Widget, *_: Any) -> Any:
        return hide_on_delete(widget)
