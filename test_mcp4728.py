from MCP4728 import MCP4728

dac_x4 = MCP4728(address=0x60, debug=True)

dac_x4.set_gain(channel=0, gain=1)
dac_x4.set_vout(channel=0, vout=1.6)
dac_x4.set_power_down(channel=0, pd=0)
dac_x4.multi_write(ch0=True)
dac_x4.read_and_print()
dac_x4.ch1_gain = 1 # vref also set to 1 when we write to gain
dac_x4.ch1_pd   = 0
dac_x4.ch1_vout = 3.8
dac_x4.single_write(channel=1)
dac_x4.read_and_print()
dac_x4.ch2_gain = 1
dac_x4.ch2_pd   = 0
dac_x4.ch2_vout = 2.1
dac_x4.ch3_gain = 1
dac_x4.ch3_pd   = 0
dac_x4.ch3_vout = 0.8
dac_x4.update_values()
dac_x4.multi_write(ch2=True, ch3=True)
dac_x4.read_and_print()
dac_x4.write_eeprom_all_off()
dac_x4.read_and_print()
