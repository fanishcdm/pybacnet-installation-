#!/usr/bin/python
"""
This file is part of pybacnet.

pybacnet is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

pybacnet is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with pybacnet.  If not, see <http://www.gnu.org/licenses/>.
"""
"""
Copyright (c) 2013 Building Robotics, Inc.
"""
"""
@author Stephen Dawson-Haggerty <steve@buildingrobotics.com>
"""

import sys
from operator import itemgetter
from pybacnet import bacnet
import optparse
import json
import datetime

def process_point(dev, obj):
  # Special cases for different control systems

  # WattStopper relays
  if dev.startswith('WS') and \
    (obj.startswith('RELAY') or obj.startswith('GROUP')):
    return bacnet.BACNET_APPLICATION_TAG_ENUMERATED
  # Siemens
  elif obj == 'HEAT.COOL':
    return bacnet.BACNET_APPLICATION_TAG_ENUMERATED
  else:
    return bacnet.BACNET_APPLICATION_TAG_REAL

def main():
  parser = optparse.OptionParser()
  parser.add_option('-i', '--interface', dest='interface',
                    default=None,
                    help='Network interface to broadcast over')
  parser.add_option('-p', '--ip-filter', dest='fip', default=None,
                    help='Filter devices by IP prefix')

  opts, args = parser.parse_args()
  filename = args[0] if len(args) else '-'
  if filename != '-':
    fout = open("/home/fanish/manasafan/pybacnet/tools/test.json", 'wb')
  else:
    fout = open("/home/fanish/manasafan/pybacnet/tools/test.json", 'wb')
#fout = sys.stdout
  print(opts)
  # MUST USE default port for whois
  bacnet.Init(opts.interface, None)

  device_list = []
  # Discover and store devices
  print(bacnet)
  devs = bacnet.whois(2)
  print >>sys.stderr, "Found", len(devs), "devices"

  for h_dev in sorted(devs, key=itemgetter('device_id')):
    # IP filter
    mac = '.'.join([str(i) for i in h_dev['mac']])
    if not opts.fip or mac.startswith(opts.fip):
      # Dev filter
      objs = []
      obj_count = bacnet.read_prop(h_dev, bacnet.OBJECT_DEVICE, h_dev['device_id'], bacnet.PROP_OBJECT_LIST, 0)
      name = bacnet.read_prop(h_dev, bacnet.OBJECT_DEVICE, h_dev['device_id'], bacnet.PROP_OBJECT_NAME, -1)
      try:
        desc = bacnet.read_prop(h_dev, bacnet.OBJECT_DEVICE, h_dev['device_id'], bacnet.PROP_DESCRIPTION, -1)
      except IOError:
        desc = None

      device = {
        'props': h_dev,
        'name': name,
        'desc': desc,
        'objs': []
        }

      if obj_count == 0:
        print >>sys.stderr, "No objects found:", d
        continue

      # Get object props and names
      for i in range(1, obj_count+1):
        h_obj = bacnet.read_prop(h_dev, bacnet.OBJECT_DEVICE, h_dev['device_id'], bacnet.PROP_OBJECT_LIST, i)
        if h_obj == None:
          print >>sys.stderr, "Object not found:", i
          continue
        try:
          name = bacnet.read_prop(h_dev, h_obj['type'], h_obj['instance'], bacnet.PROP_OBJECT_NAME, -1)
        except IOError:
          name = None
        try:
          desc = bacnet.read_prop(h_dev, h_obj['type'], h_obj['instance'], bacnet.PROP_DESCRIPTION, -1)
        except IOError:
          desc = None
        try:
          unit = bacnet.read_prop(h_dev, h_obj['type'], h_obj['instance'], bacnet.PROP_UNITS, -1)
        except IOError:
          unit = None
        try:
	      value = bacnet.read_prop(h_dev, h_obj['type'], h_obj['instance'], bacnet.PROP_PRESENT_VALUE, -1)
        except IOError:
	      value = None

        now = datetime.datetime.now()
        date_time = now.strftime("%Y-%m-%d %H:%M")
        device['objs'].append({
          'props': h_obj,
          'name': name,
          'desc': desc,
          'unit': unit,
          'data_type': process_point(device['name'], name),
	      'value': value,
          'date_time': date_time
          })
      print >>sys.stderr, device['name'], "has", len(device['objs']), "objects"
      device_list.append(device)
  json.dump(device_list, fout)
  print(device_list)
  fout.close()

if __name__ == "__main__":
  main()
