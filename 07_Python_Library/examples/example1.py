from sciencemode3 import sciencemode
import time


ack = sciencemode.ffi.new("Smpt_ack*")
device = sciencemode.ffi.new("Smpt_device*")
version_ack = sciencemode.ffi.new("Smpt_get_version_ack*")

com_connected = False
com_port_number = 1
while not com_connected:
    com = sciencemode.ffi.new("char[]", bytes("COM{0}".format(com_port_number), "utf-8"))
    ret = sciencemode.smpt_check_serial_port(com)
    print("Port check is {}", ret)
    if ret==False:
        com_port_number += 1
    else:
        com_connected = True
    
        

ret = sciencemode.smpt_open_serial_port(device,com)
print("smpt_open_serial_port: {}", ret)

packet_number = sciencemode.smpt_packet_number_generator_next(device)
print("next packet_number {}", packet_number)

ret = sciencemode.smpt_send_get_version_main(device, packet_number)
print("smpt_send_get_version_main: {}", ret)

ret = False

while ( not sciencemode.smpt_new_packet_received(device)):
    time.sleep(1)

sciencemode.smpt_last_ack(device, ack);
print("command number {}, packet_number {}", ack.command_number, ack.packet_number)

ret = sciencemode.smpt_get_get_version_main_ack(device, version_ack)
print("smpt_get_get_version_main_ack: {}", ret)
print("Firmware %d.%d.%d" % (version_ack.uc_version.fw_version.major, version_ack.uc_version.fw_version.minor, version_ack.uc_version.fw_version.revision))
print("SMPT %d.%d.%d" % (version_ack.uc_version.smpt_version.major, version_ack.uc_version.smpt_version.minor, version_ack.uc_version.smpt_version.revision))


ll_init = sciencemode.ffi.new("Smpt_ll_init*")
ll_init.high_voltage_level = sciencemode.Smpt_High_Voltage_Default
ll_init.packet_number = sciencemode.smpt_packet_number_generator_next(device)
ret = sciencemode.smpt_send_ll_init(device, ll_init)
print("smpt_send_ll_init: {}", ret)
time.sleep(1)

packet_number = sciencemode.smpt_packet_number_generator_next(device)
print("next packet_number {}", packet_number)


ll_config = sciencemode.ffi.new("Smpt_ll_channel_config*")

ll_config.enable_stimulation = True
ll_config.channel = sciencemode.Smpt_Channel_Red
ll_config.number_of_points = 3
ll_config.points[0].time = 100
ll_config.points[0].current = 20
ll_config.points[1].time = 100
ll_config.points[1].current = 20
ll_config.points[2].time = 100
ll_config.points[2].current = -20


for i in range(3):
    ll_config.packet_number = sciencemode.smpt_packet_number_generator_next(device)
    ret = sciencemode.smpt_send_ll_channel_config(device, ll_config)
    print("smpt_send_ll_channel_config: {}", ret)
    time.sleep(1)

packet_number = sciencemode.smpt_packet_number_generator_next(device)
ret = sciencemode.smpt_send_ll_stop(device, packet_number)
print("smpt_send_ll_stop: {}", ret)

ml_init = sciencemode.ffi.new("Smpt_ml_init*")
ml_init.packet_number = sciencemode.smpt_packet_number_generator_next(device)
ret = sciencemode.smpt_send_ml_init(device, ml_init)
print("smpt_send_ml_init: {}", ret)
time.sleep(1)

ml_update = sciencemode.ffi.new("Smpt_ml_update*")
ml_update.packet_number = sciencemode.smpt_packet_number_generator_next(device)
for i in range(4):
    ml_update.enable_channel[i] = True
    ml_update.channel_config[i].period = 20
    ml_update.channel_config[i].number_of_points = 3
    ml_update.channel_config[i].points[0].time = 100
    ml_update.channel_config[i].points[0].current = 20
    ml_update.channel_config[i].points[1].time = 100
    ml_update.channel_config[i].points[1].current = 20
    ml_update.channel_config[i].points[2].time = 100
    ml_update.channel_config[i].points[2].current = -20
    
ret = sciencemode.smpt_send_ml_update(device, ml_update)
print("smpt_send_ml_update: {}", ret)

ml_get_current_data = sciencemode.ffi.new("Smpt_ml_get_current_data*")


for i in range(10):
    ml_get_current_data.data_selection[1] = True
    ml_get_current_data.packet_number = sciencemode.smpt_packet_number_generator_next(device)
    ret = sciencemode.smpt_send_ml_get_current_data(device, ml_get_current_data)
    print("smpt_send_ml_get_current_data: {}", ret)
    time.sleep(1)


packet_number = sciencemode.smpt_packet_number_generator_next(device)
ret = sciencemode.smpt_send_ml_stop(device, packet_number)
print("smpt_send_ml_stop: {}", ret)


ret = sciencemode.smpt_close_serial_port(device)
print("smpt_close_serial_port: {}", ret)