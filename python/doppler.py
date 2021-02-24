#!/usr/bin/env python
'''
   Copyright 2021 Fran Acien

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
'''
from gnuradio import gr
import sys
import threading
import time
import socket
import pmt
from doppler.multiple_source import MultipleEtcTLESource
from orbit_predictor.locations import Location

class doppler_runner(threading.Thread):
  def __init__(self, bc, predictor, gndlocation, verbose):
    threading.Thread.__init__(self)

    self.predictor = predictor
    self.gndlocation = gndlocation
    self.verbose = verbose
    self.blockclass = bc

    self.stopThread = False
    self.clientConnected = False
    self.sock = None
    self.server = None

  def run(self):
    while not self.stopThread:
      doppler = self.gndlocation.doppler_factor(self.predictor.get_position())
      if self.verbose: print("[doppler] factor %.10f" % doppler)
      self.blockclass.sendFactor(doppler)
      time.sleep(0.5)

class doppler(gr.sync_block):
  def __init__(self, lat, long, alt, sat_id, tle_file, verbose):
    gr.sync_block.__init__(self, name = "Doppler", in_sig = None, out_sig = None)

    # Init block variables
    self.lat = lat
    self.long = long
    self.alt = alt
    self.sat_id = sat_id
    self.tle_file = tle_file

    gndlocation=Location(
        "GND", latitude_deg=float(self.lat), longitude_deg=float(self.long), elevation_m=float(self.alt))
    print(gndlocation)
    source = MultipleEtcTLESource(filename=tle_file)
    predictor = source.get_predictor(self.sat_id)

    self.thread = doppler_runner(self, predictor, gndlocation, verbose)
    self.thread.start()
    self.message_port_register_out(pmt.intern("factor"))
    self.message_port_register_out(pmt.intern("state"))

  def stop(self):
    self.thread.stopThread = True

    self.thread.join()

    return True

  def sendFactor(self,factor):
    p = pmt.from_float(factor)
    self.message_port_pub(pmt.intern("factor"),pmt.cons(pmt.intern("factor"),p))

  def sendState(self,state):
    if (state):
      newState = 1
    else:
      newState = 0

    self.message_port_pub(pmt.intern("state"),pmt.cons( pmt.intern("state"), pmt.from_long(newState) ))
