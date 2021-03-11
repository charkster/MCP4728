#!/usr/bin/python
from __future__ import print_function
import time
import smbus

# ============================================================================
# MCP4728 4 channel 12-Bit DAC
# ============================================================================

class MCP4728 :
	i2c = None
  
	# Commands (all below values have been shifted left by 3)
	__MULTI_WRITE_CMD       = 0x40 # registers only
	__SEQ_WRITE_BOTH_CMD    = 0x50 # registers and eeprom
	__SINGLE_WRITE_BOTH_CMD = 0x58 # registers and eeprom
	__VREF_WRITE_CMD        = 0x80 # registers only
	__GAIN_WRITE_CMD        = 0xC0 # registers only
	__PD_WRITE_CMD          = 0xA0 # registers only
  
	# Constants
	__DAC_MAX_VAL           = 4095  # 12bit DAC
	__MAX_EXT_VCC           = 5.5   # 5.5V from the datasheet

	# Constructor, this is also used to store settings before they are written to the device
	def __init__(self, address=0x60, debug=False):
		self.i2c           = smbus.SMBus(1)
		self.address       = address
		self.ch0_vout      = 0.0     # voltage to output, must be less than dac_vcc for external ref, must be less than 2.048 << gain for internal ref
		self.ch0_ext_vcc   = 3.3     # this is the external vcc voltage, it will be ignored if vref == 1
		self.ch0_gain      = 1       # internal gain bit: 0 is x1, 1 is x2
		self.ch0_vref      = 1       # 1 is use internal ref, 0 is external ref
		self.ch0_pd        = 1       # power down: 0 is DAC enabled, 1 is DAC disabled with 1k pulldown, 2 is DAC disabled with 100k pulldown, 3 is DAC disabled with 500k pulldown
		self.ch1_vout      = 0.0
		self.ch1_ext_vcc   = 3.3
		self.ch1_gain      = 1
		self.ch1_vref      = 1
		self.ch1_pd        = 1
		self.ch2_vout      = 0.0
		self.ch2_ext_vcc   = 3.3
		self.ch2_gain      = 1
		self.ch2_vref      = 1
		self.ch2_pd        = 1
		self.ch3_vout      = 0.0
		self.ch3_ext_vcc   = 3.3
		self.ch3_gain      = 1
		self.ch3_vref      = 1
		self.ch3_pd        = 1
		self.debug         = debug
		self.ch0_vcc       = 0.0
		self.ch1_vcc       = 0.0
		self.ch2_vcc       = 0.0
		self.ch3_vcc       = 0.0
		self.ch0_dac_val   = 0x000
		self.ch1_dac_val   = 0x000
		self.ch2_dac_val   = 0x000
		self.ch3_dac_val   = 0x000
		self.ch0_cfg_byte  = 0x00
		self.ch1_cfg_byte  = 0x00
		self.ch2_cfg_byte  = 0x00
		self.ch3_cfg_byte  = 0x00
		self.ch0_cfg_fast_byte = 0x00
		self.ch1_cfg_fast_byte = 0x00
		self.ch2_cfg_fast_byte = 0x00
		self.ch3_cfg_fast_byte = 0x00
		self.ch0_dac_byte  = 0x00
		self.ch1_dac_byte  = 0x00
		self.ch2_dac_byte  = 0x00
		self.ch3_dac_byte  = 0x00

	# update the vcc, dac_val, cfg_byte, cfg_fast_byte and dac_bytes in the constructor space
	def update_values(self):
		if (self.debug == True):
			print("MCP4728 update_values")
		self.ch0_vcc       = self.ch0_ext_vcc if self.ch0_vref == 0 else 2.048 * (self.ch0_gain + 1)
		self.ch1_vcc       = self.ch1_ext_vcc if self.ch1_vref == 0 else 2.048 * (self.ch1_gain + 1)
		self.ch2_vcc       = self.ch2_ext_vcc if self.ch2_vref == 0 else 2.048 * (self.ch2_gain + 1)
		self.ch3_vcc       = self.ch3_ext_vcc if self.ch3_vref == 0 else 2.048 * (self.ch3_gain + 1)
		self.ch0_dac_val   = int(self.ch0_vout / self.ch0_vcc * self.__DAC_MAX_VAL)
		self.ch1_dac_val   = int(self.ch1_vout / self.ch1_vcc * self.__DAC_MAX_VAL)
		self.ch2_dac_val   = int(self.ch2_vout / self.ch2_vcc * self.__DAC_MAX_VAL)
		self.ch3_dac_val   = int(self.ch3_vout / self.ch3_vcc * self.__DAC_MAX_VAL)
		self.ch0_cfg_byte  = ((self.ch0_vref << 7) + (self.ch0_pd << 5) + (self.ch0_gain << 4) + (self.ch0_dac_val >> 8)) & 0xFF
		self.ch1_cfg_byte  = ((self.ch1_vref << 7) + (self.ch1_pd << 5) + (self.ch1_gain << 4) + (self.ch1_dac_val >> 8)) & 0xFF
		self.ch2_cfg_byte  = ((self.ch2_vref << 7) + (self.ch2_pd << 5) + (self.ch2_gain << 4) + (self.ch2_dac_val >> 8)) & 0xFF
		self.ch3_cfg_byte  = ((self.ch3_vref << 7) + (self.ch3_pd << 5) + (self.ch3_gain << 4) + (self.ch3_dac_val >> 8)) & 0xFF
		self.ch0_cfg_fast_byte = ((self.ch0_pd << 4) + (self.ch0_dac_val >> 8)) & 0xFF
		self.ch1_cfg_fast_byte = ((self.ch1_pd << 4) + (self.ch1_dac_val >> 8)) & 0xFF
		self.ch2_cfg_fast_byte = ((self.ch2_pd << 4) + (self.ch2_dac_val >> 8)) & 0xFF
		self.ch3_cfg_fast_byte = ((self.ch3_pd << 4) + (self.ch3_dac_val >> 8)) & 0xFF
		self.ch0_dac_byte  = self.ch0_dac_val & 0xFF
		self.ch1_dac_byte  = self.ch1_dac_val & 0xFF
		self.ch2_dac_byte  = self.ch2_dac_val & 0xFF
		self.ch3_dac_byte  = self.ch3_dac_val & 0xFF
	
	# fast write updates all channels, but does not write to VREF or GAIN
	def fast_write(self):
		if (self.debug == True):
			print("MCP4728 fast_write")
		self.update_values()  # calculate the vcc, dac_val, cfg_byte, cfg_fast_byte, dac_byte before writing
		self.i2c.write_i2c_block_data(self.address, self.ch0_cfg_fast_byte, [self.ch0_dac_byte, self.ch1_cfg_fast_byte, self.ch1_dac_byte, \
		                                            self.ch2_cfg_fast_byte,  self.ch2_dac_byte, self.ch3_cfg_fast_byte, self.ch3_dac_byte ])
	
	# multi channel allows any number of channels to be written to 
	def multi_write(self, ch0=False, ch1=False, ch2=False, ch3=False, udac=0):
		if (self.debug == True):
			print("MCP4728 multi_write")
		if (ch0==False and ch1==False and ch2==False and ch3==False):
			print("ERROR at least one channel must be set True")
			return -1
		if (udac != 0 and udac != 1):
			print("ERROR udac must be either 0 (update all DACs at the end) or 1 (update DACs immediately)")
			return -1
		self.update_values() # calculate the vcc, dac_val, cfg_byte, cfg_fast_byte, dac_byte before writing
		write_bytes = []
		if (ch0 == True):
			write_bytes.append(self.__MULTI_WRITE_CMD + (0x00 << 1) + udac)
			write_bytes.append(self.ch0_cfg_byte)
			write_bytes.append(self.ch0_dac_byte)
		if (ch1 == True):
			write_bytes.append(self.__MULTI_WRITE_CMD + (0x01 << 1) + udac)
			write_bytes.append(self.ch1_cfg_byte)
			write_bytes.append(self.ch1_dac_byte)
		if (ch2 == True):
			write_bytes.append(self.__MULTI_WRITE_CMD + (0x02 << 1) + udac)
			write_bytes.append(self.ch2_cfg_byte)
			write_bytes.append(self.ch2_dac_byte)
		if (ch3 == True):
			write_bytes.append(self.__MULTI_WRITE_CMD + (0x03 << 1) + udac)
			write_bytes.append(self.ch3_cfg_byte)
			write_bytes.append(self.ch3_dac_byte)
		self.i2c.write_i2c_block_data(self.address, write_bytes[0], write_bytes[1:])
		
	# the single write will write both to registers and eeprom
	def single_write(self, channel=0, udac=0):
		if (channel > 4 or channel < 0):
			print("Channel must be 0, 1, 2, or 3")
			return -1
		if (udac != 0 and udac != 1):
			print("ERROR udac must be either 0 (update all DACs at the end) or 1 (update DACs immediately)")
			return -1
		self.update_values()  # calculate the vcc, dac_val, cfg_byte, cfg_fast_byte, dac_byte before writing
		byte0 = self.__SINGLE_WRITE_BOTH_CMD + (channel << 1) + udac
		if (channel == 0):
			self.i2c.write_i2c_block_data(self.address, byte0 ,[self.ch0_cfg_byte, self.ch0_dac_byte])
		elif (channel == 1):
			self.i2c.write_i2c_block_data(self.address, byte0 ,[self.ch1_cfg_byte, self.ch1_dac_byte])
		elif (channel == 2):
			self.i2c.write_i2c_block_data(self.address, byte0 ,[self.ch2_cfg_byte, self.ch2_dac_byte])
		elif (channel == 3):
			self.i2c.write_i2c_block_data(self.address, byte0 ,[self.ch3_cfg_byte, self.ch3_dac_byte])
		time.sleep(0.5)
	
	def write_eeprom_all_off(self):
		if (self.debug == True):
			print("MCP4728 write_eeprom_all_off")
		self.ch0_gain = 0
		self.ch1_gain = 0
		self.ch2_gain = 0
		self.ch3_gain = 0
		self.ch0_pd   = 3
		self.ch1_pd   = 3
		self.ch2_pd   = 3
		self.ch3_pd   = 3
		self.ch0_vref = 0
		self.ch1_vref = 0
		self.ch2_vref = 0
		self.ch3_vref = 0
		self.ch0_vout = 3.3
		self.ch1_vout = 3.3
		self.ch2_vout = 3.3
		self.ch3_vout = 3.3
		self.seq_write(channel=0)
	
	# if channel = 3, only channel 3 will be written. if channel = 2, channels 2 & 3 will be written. if channel = 1, channels 1,2 & 3 will be written. if channel = 0 all channels will be written
	def seq_write(self, channel=0, udac=0):
		if (self.debug == True):
			print("MCP4728 seq_write")
		if (channel > 4 or channel < 0):
			print("Channel must be 0, 1, 2, or 3")
			return -1
		if (udac != 0 and udac != 1):
			print("ERROR udac must be either 0 (update all DACs at the end) or 1 (update DACs immediately)")
			return -1
		self.update_values() # calculate the vcc, dac_val, cfg_byte, cfg_fast_byte, dac_byte before writing
		write_bytes = []
		if (channel==0):
			write_bytes.append(self.__SEQ_WRITE_BOTH_CMD + (0x00 << 1) + udac)
			write_bytes.append(self.ch0_cfg_byte)
			write_bytes.append(self.ch0_dac_byte)
		if (channel < 2):
			if (channel == 1):
				write_bytes.append(self.__SEQ_WRITE_BOTH_CMD + (0x01 << 1) + udac)
			write_bytes.append(self.ch1_cfg_byte)
			write_bytes.append(self.ch1_dac_byte)
		if (channel < 3):
			if (channel == 2):
				write_bytes.append(self.__SEQ_WRITE_BOTH_CMD + (0x02 << 1) + udac)
			write_bytes.append(self.ch2_cfg_byte)
			write_bytes.append(self.ch2_dac_byte)
		if (channel < 4):
			if (channel == 3):
				write_bytes.append(self.__SEQ_WRITE_BOTH_CMD + (0x03 << 1) + udac)
			write_bytes.append(self.ch3_cfg_byte)
			write_bytes.append(self.ch3_dac_byte)
		self.i2c.write_i2c_block_data(self.address, write_bytes[0], write_bytes[1:])
		time.sleep(0.5)
		
	def read_and_print(self):
		if (self.debug == True):
			print("MCP4728 read_all_registers")
		read_list= []
		read_list = self.i2c.read_i2c_block_data(self.address, 0x00, 24)
		vref_list = [None] * 8
		gain_list = [None] * 8
		pd_list   = [None] * 8
		dac_list  = [None] * 8
		vref_list[0] = (read_list[1]  >> 7) & 0x01
		vref_list[4] = (read_list[4]  >> 7) & 0x01 # eeprom
		vref_list[1] = (read_list[7]  >> 7) & 0x01
		vref_list[5] = (read_list[10] >> 7) & 0x01 # eeprom
		vref_list[2] = (read_list[13] >> 7) & 0x01
		vref_list[6] = (read_list[16] >> 7) & 0x01 # eeprom
		vref_list[3] = (read_list[19] >> 7) & 0x01
		vref_list[7] = (read_list[22] >> 5) & 0x01 # eeprom
		pd_list[0]   = (read_list[1]  >> 5) & 0x03
		pd_list[4]   = (read_list[4]  >> 5) & 0x03 # eeprom
		pd_list[1]   = (read_list[7]  >> 5) & 0x03
		pd_list[5]   = (read_list[10] >> 5) & 0x03 # eeprom
		pd_list[2]   = (read_list[13] >> 5) & 0x03
		pd_list[6]   = (read_list[16] >> 5) & 0x03 # eeprom
		pd_list[3]   = (read_list[19] >> 5) & 0x03
		pd_list[7]   = (read_list[22] >> 5) & 0x03 # eeprom
		gain_list[0] = (read_list[1]  >> 4) & 0x01
		gain_list[4] = (read_list[4]  >> 4) & 0x01 # eeprom
		gain_list[1] = (read_list[7]  >> 4) & 0x01
		gain_list[5] = (read_list[10] >> 4) & 0x01 # eeprom
		gain_list[2] = (read_list[13] >> 4) & 0x01
		gain_list[6] = (read_list[16] >> 4) & 0x01 # eeprom
		gain_list[3] = (read_list[19] >> 4) & 0x01
		gain_list[7] = (read_list[22] >> 4) & 0x01 # eeprom
		dac_list[0]  = ((read_list[1]  & 0x0F) << 8) + read_list[2]
		dac_list[4]  = ((read_list[4]  & 0x0F) << 8) + read_list[5] # eeprom
		dac_list[1]  = ((read_list[7]  & 0x0F) << 8) + read_list[8]
		dac_list[5]  = ((read_list[10] & 0x0F) << 8) + read_list[11] # eeprom
		dac_list[2]  = ((read_list[13] & 0x0F) << 8) + read_list[14]
		dac_list[6]  = ((read_list[16] & 0x0F) << 8) + read_list[17] # eeprom
		dac_list[3]  = ((read_list[19] & 0x0F) << 8) + read_list[20]
		dac_list[7]  = ((read_list[22] & 0x0F) << 8) + read_list[23] # eeprom
		for channel in range(0,4):
			print("Channel {}, VREF = {}, PD = {}, GAIN = {}, DAC = 0x{:02x}".format(channel,vref_list[channel],pd_list[channel],gain_list[channel],dac_list[channel]))
		for channel in range(0,4):
			print("EEPROM Channel {}, VREF = {}, PD = {}, GAIN = {}, DAC = 0x{:03x}".format(channel,vref_list[channel+4],pd_list[channel+4],gain_list[channel+4],dac_list[channel+4]))
	
	# this does not write to the device, but gets the value ready for a multi_write or seq_write
	def set_vref(self, channel=0, vref=1):
		if (self.debug == True):
			print("MCP4728 set_vref, channel given is {0}, vref given is {1}".format(channel,vref))
		if (channel > 4 or channel < 0):
			print("Channel must be 0, 1, 2, or 3")
			return -1
		if (vref != 0 and vref != 1):
			print("Vref must be 0 (external ref) or 1 (internal ref)")
			return -1
		if (channel == 0):
			self.ch0_vref = vref
		elif (channel == 1):
			self.ch1_vref = vref
		elif (channel == 2):
			self.ch2_vref = vref
		elif (channel == 3):
			self.ch3_vref = vref
		self.update_values()
	
	# this does not write to the device, but gets the value ready for a multi_write or seq_write
	def set_ext_vcc(self, channel=0, vcc=0.0):
		if (self.debug == True):
			print("MCP4728 set_ext_vcc, channel given is {}, vcc given is {}".format(channel,vcc))
		if (channel > 4 or channel < 0):
			print("Channel must be 0, 1, 2, or 3")
			return -1
		if (vcc < 0.0 or vcc > self.__MAX_EXT_VCC):
			print("External Vcc must be between 0 and {:.2f}V".format(self.__MAX_EXT_VCC))
			return -1
		if (channel == 0):
			self.ch0_ext_vcc = vcc
			self.ch0_vref = 0 # if we are using external_vcc, that only applies to external ref
		elif (channel == 1):
			self.ch1_ext_vcc = vcc
			self.ch1_vref = 0
		elif (channel == 2):
			self.ch2_ext_vcc = vcc
			self.ch2_vref = 0
		elif (channel == 3):
			self.ch3_ext_vcc = vcc
			self.ch3_vref = 0
		self.update_values()
	
	# this does not write to the device, but gets the value ready for a multi_write or seq_write
	def set_gain(self, channel=0, gain=0):
		if (self.debug == True):
			print("MCP4728 set_gain, channel given is {}, gain given is {}".format(channel,gain))
		if (channel > 4 or channel < 0):
			print("Channel must be 0, 1, 2, or 3")
			return -1
		if (gain != 0 and gain != 1):
			print("Gain must be 0 (x1) or 1 (x2)")
			return -1
		if (channel == 0):
			self.ch0_gain = gain
			self.ch0_vref = 1 # if we are using the gain, that only applies to internal ref
		elif (channel == 1):
			self.ch1_gain = gain
			self.ch1_vref = 1
		elif (channel == 2):
			self.ch2_gain = gain
			self.ch2_vref = 1
		elif (channel == 3):
			self.ch3_gain = gain
			self.ch3_vref = 1
		self.update_values()
	
	# this does not write to the device, but gets the value ready for a multi_write, seq_write or fast write
	def set_power_down(self, channel=0, pd=0):
		if (self.debug == True):
			print("MCP4728 set_power_down, channel given is {}, pd given is {}".format(channel,pd))
		if (channel > 4 or channel < 0):
			print("Channel must be 0, 1, 2, or 3")
			return -1
		if (pd < 0 or pd > 3):
			print("Power down must be 0 (vout enabled), 1 (1k pulldown), 2 (100k pulldown) or 3 (500k pulldown)")
			return -1
		if (channel == 0):
			self.ch0_pd = pd
		elif (channel == 1):
			self.ch1_pd = pd
		elif (channel == 2):
			self.ch2_pd = pd
		elif (channel == 3):
			self.ch3_pd = pd
		self.update_values()
	
	# this does not write to the device, but gets the value ready for a multi_write, seq_write or fast write
	def set_vout(self, channel=0, vout=0.0):
		if (self.debug == True):
			print("MCP4728 set_vout, channel given is {}, vout given is {:0.3f}".format(channel,vout))
		if (channel > 4 or channel < 0):
			print("Channel must be 0, 1, 2, or 3")
			return -1
		if (channel == 0):
			if (vout > self.ch0_vcc):
				print("Error given vout of {:.03f} is greater than vcc of {:0.3f}".format(vout,self.ch0_vcc))
				return -1
			self.ch0_vout = vout
		elif (channel == 1):
			if (vout > self.ch1_vcc):
				print("Error given vout of {:.03f} is greater than vcc of {:0.3f}".format(vout,self.ch1_vcc))
				return -1
			self.ch1_vout = vout
		elif (channel == 2):
			if (vout > self.ch2_vcc):
				print("Error given vout of {:.03f} is greater than vcc of {:0.3f}".format(vout,self.ch2_vcc))
				return -1
			self.ch2_vout = vout
		elif (channel == 3):
			if (vout > self.ch3_vcc):
				print("Error given vout of {:.03f} is greater than vcc of {:0.3f}".format(vout,self.ch3_vcc))
				return -1
			self.ch3_vout = vout
		self.update_values()
		
