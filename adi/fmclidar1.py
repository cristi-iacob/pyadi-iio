# Copyright (C) 2019 Analog Devices, Inc.
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#     - Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     - Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in
#       the documentation and/or other materials provided with the
#       distribution.
#     - Neither the name of Analog Devices, Inc. nor the names of its
#       contributors may be used to endorse or promote products derived
#       from this software without specific prior written permission.
#     - The use of this software may or may not infringe the patent rights
#       of one or more patent holders.  This license does not release you
#       from the requirement that you obtain separate licenses from these
#       patent holders to use this software.
#     - Use of the software either in source or binary form, must be run
#       on or directly connected to an Analog Devices Inc. component.
#
# THIS SOFTWARE IS PROVIDED BY ANALOG DEVICES "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, NON-INFRINGEMENT, MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED.
#
# IN NO EVENT SHALL ANALOG DEVICES BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, INTELLECTUAL PROPERTY
# RIGHTS, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
# THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from adi.ad5627 import ad5627
from adi.ad9094 import ad9094
from adi.rx_tx import phy
import numpy as np

class fmclidar1 (ad5627, ad9094, phy):
    """ LiDAR """
    _device_name = "LiDAR"

    def __init__(self, uri, pulse_capture_address="7c700000"):
        ad5627.__init__(self, uri)
        ad9094.__init__(self, uri)
        # The name of the pulse capture channel. The address might be different,
        # depending on how the board was built.
        self.pulse_capture = pulse_capture_address + "." + "axi-pulse-capture"
        self._ctrl = self._ctx.find_device(self.pulse_capture)
        self.set_all_iio_attrs_to_default_values()

    def rx(self):
        """Read the buffers for all the enabled channels, except Channel4 which should
        be all zeroes and not relevant for the user.
        """
        ret = []
        for channel in super().rx():
            cast_channel = channel.astype(np.int8)
            # Ignore Channel4 and add everything else.
            if not np.all(cast_channel==0):
                ret.append(cast_channel)
        return ret

    def laser_enable(self):
        """Enable the laser."""
        self._set_iio_attr_int("altvoltage0", "en", True, 1, self._ctrl)

    def laser_disable(self):
        """Disable the laser."""
        self._set_iio_attr_int("altvoltage0", "en", True, 0, self._ctrl)


    @property
    def laser_pulse_width(self):
        """Get the laser pulse width, in ns."""
        return self._get_iio_attr("altvoltage0", "pulse_width_ns", True, self._ctrl)

    @laser_pulse_width.setter
    def laser_pulse_width(self, width):
        """Set the laser pulse width, in ns."""
        self._set_iio_attr_int("altvoltage0", "pulse_width_ns", True, width, self._ctrl)


    @property
    def laser_frequency(self):
        """Get the laser frequency."""
        return self._get_iio_attr("altvoltage0", "frequency", True, self._ctrl)

    @laser_frequency.setter
    def laser_frequency(self, frequency):
        """Set the laser frequency."""
        self._set_iio_attr_int("altvoltage0", "frequency", True, frequency, self._ctrl)


    @property
    def channel_sequencer_enable_disable(self):
        """Get the status of the channel sequencer (enable/disable)."""
        return self._get_iio_dev_attr("sequencer_en")

    @channel_sequencer_enable_disable.setter
    def channel_sequencer_enable_disable(self, status):
        """Enable/disable the channel sequencer. Status = 0 to disable, 1 to enable the
        sequencer.
        """
        self._set_iio_dev_attr_str("sequencer_en", status, self._ctrl)


    @property
    def channel_sequencer_opmode(self):
        """Get the channel sequencer operation mode."""
        return self._get_iio_dev_attr("sequencer_mode")

    @channel_sequencer_opmode.setter
    def channel_sequencer_opmode(self, mode):
        """Set the channel sequencer operation mode. mode = \"auto\" for auto mode and
        \"manual\" for manual mode.
        """
        self._set_iio_dev_attr_str("sequencer_mode", mode, self._ctrl)


    @property
    def channel_sequencer_order_auto_mode(self):
        """Set the channels order when in auto mode."""
        return self._get_iio_dev_attr("sequencer_auto_cfg")

    @channel_sequencer_order_auto_mode.setter
    def channel_sequencer_order_auto_mode(self, order):
        """Set the channels order when in auto mode. Order is a string with the four
        channels separated by spaces (i.e. \"3 2 0 1\")
        """
        self._set_iio_dev_attr_str("sequencer_auto_cfg", order, self._ctrl)


    @property
    def channel_sequencer_order_manual_mode(self):
        """Get the channels order when in manual mode."""
        return self._get_iio_dev_attr("sequencer_manual_chsel")

    @channel_sequencer_order_manual_mode.setter
    def channel_sequencer_order_manual_mode(self, order):
        """Set the channels order when in manual mode. Order is a string with the four
        channels separated by spaces (i.e. \"3 2 0 1\")
        """
        self._set_iio_dev_attr_str("sequencer_manual_chsel", order, self._ctrl)


    @property
    def sequencer_pulse_delay(self):
        """Get the delay of the pulse sequencer, in nanoseconds"""
        return self._get_iio_dev_attr("sequencer_pulse_delay_ns")

    @sequencer_pulse_delay.setter
    def sequencer_pulse_delay(self, ns):
        """Set the delay of the pulse sequencer, in nanoseconds"""
        self._set_iio_dev_attr_str("sequencer_pulse_delay_ns", ns, self._ctrl)

    def set_all_iio_attrs_to_default_values(self):
        """Set all the Lidar attributes to reasonable default values."""
        self.channel_sequencer_enable_disable = 0
        self.channel_sequencer_opmode = "auto"
        self.channel_sequencer_order_manual_mode = "0 0 0 0"
        self.channel_sequencer_order_auto_mode = "0 1 2 3"
        self.sequencer_pulse_delay = 248
        self.laser_enable()
        self.laser_frequency = 50000
        self.laser_pulse_width = 20
        self.apdbias = -160
        self.tiltvoltage = 0
