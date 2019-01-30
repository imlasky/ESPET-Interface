# ESPET-Interface
This class will allow for the interaction of the Electrospray Engineering
Toolkit (ESPET) from Spectral Sciences Inc. 

### General Usage and Work Flow
There is a specific work flow that must be adhered to which allows for minimal
data editing and faster accessing. The work flow is below:

1. Create Object
2. Create connection to the ESPET quicksolver
3. Login with your credentials
4. Select the emitter and feed type
5. Upload data
6. Run simulation
7. Save simulation data

Below is a simple toy example:

'''
my_emitter = Emitter.Emitter()
my_emitter.create_connection()
my_emitter.login('username', 'password')
my_emitter.select_props()
my_emitter.upload_data_individual()
my_emitter.run_sim()
my_emitter.save_sim()
'''

### In progress
Currently, the only way to upload data using this class is one by one through the available
fields. However, on the ESPET site there is an option to upload a configuration
file which is in the form of a JSON dump. 


