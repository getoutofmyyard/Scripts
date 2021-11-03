import threading
from netmiko import ConnectHandler
from getpass import getpass
from queue import Queue

# Parameters for the SSH connection. Logins with priv 15 will ignore the enable_secret.
username = input("Username: ")
password = getpass("Password: ")
enable_secret = getpass("Enable secret: ")
device_type = "cisco_ios" #Change to cisco_nxos for Nexus, arista_eos for EOS, etc.
command = "show run"

# Device file is opened and split into an array of device names
device_path = "PATH/TO/DEVICE/LIST"
device_file = open(device_path)
devices = device_file.read().splitlines()

# Define number of threads to run, initialize a queue, and
# define a lock to prevent simultaneous print output
num_threads = 8
my_queue = Queue()
print_lock = threading.Lock()


# Each thread utilizes the following function to connect to devices
# and return their command output. i = thread, q = my_queue
def device_connection(i,q):

	while not queue.empty():

		# Grab a hostname from the queue
		hostname = q.get()

		# Define a device dictionary for Netmiko connections
		switch = {
			"username":username,
			"password":password,
			"secret":enable_secret,
			"device_type":device_type,
			"host":hostname
		}

		# Define the path of the resulting config backup file.
		# Each file is named after the device.
		file_path = "YOUR/PATH/HERE/{}.txt".format(hostname)

		try:

			with open(file_path,"w+") as config_file:

				# Connect to the host with Netmiko and grab command output
				connection = ConnectHandler(**switch)
				output = connection.send_command(command)

				# Informational text. print_lock is used to prevent multiple threads
				# from printing simultaneously.
				with print_lock:
					print(hostname + ": " + "Saving file {}".format(file_path))

				write_new_file = config_file.write(output)

				connection.disconnect()

			# Alerts that the thread has completed its task for this
			# item in the queue
			q.task_done()

		except Exception as exception:

			with print_lock:
				print(exception)

			q.task_done()


def main():

	# For the number of threads specified in num_threads, create a new thread
	# of device_connector(i, my_queue) and run the process as a daemon.
	for i in range(num_threads):
		thread = threading.Thread(target=device_connection, args=(i,my_queue))
		thread.setDaemon(True)
		thread.start()

	# Inject all devices in the device list into the queue
	for hostname in devices:
		my_queue.put(hostname)

	my_queue.join()

if __name__ == "__main__":

	main()
