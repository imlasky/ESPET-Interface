import os
import time
import pickle
import numpy as np
import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui  import Select

class Emitter(object):
    """Emitter object capable of automatically running ESPET website"""

    __emitters = ['Capillary_IL', 'Capillary_LM', 'External_Cone_IL',
                'External_Cone_LM', 'Framework_Toy_Demo', 'Porous_Cone_IL',
                'Porous_Cone_LM', 'Porous_Edge_IL']

    __feeds = ['Cylindrical_Channel', 'Cylindrical_External',
            'Cylindrical_Porous', 'Low_Z', 'Rectangular_Channel', 'Rectangular_Porous',
            'Tapered_Porous']

    __propellants = ['Caesium,Liquid Metal', 'EMI-BF4,Ionic Liquid',
            'EMI-GaCl4,Ionic Liquid', 'EMI-TFSI,Ionic Liquid', 'Gallium,Liquid Metal',
            'Indium,Liquid Metal']

    __independent_variables = ['T', 'V', 'P']

    __emitter_substrates = ['Aluminum,Channel',
                            'Borosilicate Glass Fibermat,Porous',
                            'Borosilicate Glass P0,Porous',
                            'Borosilicate Glass P1,Porous',
                            'Borosilicate Glass P2,Porous',
                            'Borosilicate Glass P3,Porous',
                            'Borosilicate Glass P4,Porous',
                            'Borosilicate Glass P5,Porous',
                            'Borosilicate Glass,Channel',
                            'Gold,Channel', 'Platinum,Channel',
                            'Rhenium,Channel', 'Silicon,Channel',
                            'Stainless Steel Fibermat 1,Porous',
                            'Tungsten Porous 1,Porous',
                            'Tungsten Porous 2,Porous',
                            'Tungsten,Channel',
                            'Xerogel 1,Porous']

    __feed_substrates = ['Aluminum,Channel',
                            'Borosilicate Glass Fibermat,Porous',
                            'Borosilicate Glass P0,Porous',
                            'Borosilicate Glass P1,Porous',
                            'Borosilicate Glass P2,Porous',
                            'Borosilicate Glass P3,Porous',
                            'Borosilicate Glass P4,Porous',
                            'Borosilicate Glass P5,Porous',
                            'Borosilicate Glass,Channel',
                            'Gold,Channel', 'Platinum,Channel',
                            'Rhenium,Channel', 'Silicon,Channel',
                            'Stainless Steel Fibermat 1,Porous',
                            'Tungsten Porous 1,Porous',
                            'Tungsten Porous 2,Porous',
                            'Tungsten,Channel',
                            'Xerogel 1,Porous']

    __fields = ['Mean CR of Active Sites', 'Electric Current', 'Efficiency',
                'Mass Flow', 'Thrust', 'Number of Active Sites', 'Isp',
                'Number of Sites In Ion Mode']

    def __init__(self, emitter='Capillary_IL', feed='Cylindrical_Channel',
                propellant='EMI-BF4,Ionic Liquid',
                emitter_substrate='Borosilicate Glass,Channel',
                feed_substrate='Borosilicate Glass P4,Porous',
                field='Thrust', independent_variable='V'):

        self.emitter = emitter
        self.feed = feed
        self.propellant = propellant
        self.emitter_substrate = emitter_substrate
        self.feed_substrate = feed_substrate
        self.field = field
        self.independent_variable = independent_variable

    def create_connection(self):
        """Connect to the ESPET quicksolver"""

        chrome_options = webdriver.ChromeOptions()
        prefs = {'download.default_directory' : os.getcwd() + '/output_data/'}
        chrome_options.add_experimental_option('prefs', prefs)

        self.driver = webdriver.Chrome(ChromeDriverManager().install(),
                chrome_options=chrome_options)
        self.driver.get('http://espet.spectral.com/espet/qsolver/')

    def login(self, username, password):
        """Log into the ESPET quicksolver"""

        self.driver.find_element_by_name('username').send_keys(username)
        self.driver.find_element_by_name('password').send_keys(password)
        self.driver.find_element_by_xpath('/html/body/form/input[2]').click()

    def select_props(self):
        """Select the emitter, feed, and independent variable"""

        emitter_select = Select(self.driver.find_element_by_name('emitter'))
        emitter_select.select_by_value(self._emitter)

        feed_select = Select(self.driver.find_element_by_name('feed'))
        feed_select.select_by_value(self._feed)

        independent_variable_select = Select(self.driver.find_element_by_name('independentVariable'))
        independent_variable_select.select_by_value(self._independent_variable)

        try:
            self.__get_fields()
        except:
            self.scrape_fields()
            self.save_fields()

    def __get_fields(self):
        """Upload dictionary of fields given emitter and feed combination"""

        if not os.path.exists('input_field_files'):
            os.makedirs('input_field_files')

        try:
            fname = ('./input_field_files/' + self._emitter + '_and_' +
                    self._feed + '_with_' + self._independent_variable +
                    '.pickle')
            with open(fname, 'rb') as f:
                self._input_fields = pickle.load(f)
        except FileNotFoundError:
            pass


    def scrape_fields(self):
        """Scrape available fields given feed and emitter and feed
        combination"""

        propellant_options  = Select(self.driver.find_element_by_name('propellant')).options
        emitter_substrate_options = Select(self.driver.find_element_by_name('substrate_emitter')).options
        feed_substrate_options = Select(self.driver.find_element_by_name('substrate_feed')).options

        self.__propellants = [str(o.get_attribute('value')) for o in propellant_options if not
                o.get_attribute('disabled')]

        self.__emitter_substrates = [str(o.get_attribute('value')) for o in
                emitter_substrate_options if not o.get_attribute('disabled')]

        self.__feed_substrates = [str(o.get_attribute('value')) for o in
                feed_substrate_options if not o.get_attribute('disabled')]

        input_fields = self.driver.find_elements_by_xpath("//input[@type='text']")
        field_names = [str(i.get_attribute('name')) for i in input_fields if not
                i.get_attribute('readonly')]
        field_vals = [str(i.get_attribute('value')) for i in input_fields if not
                i.get_attribute('readonly')]

        self._input_fields = dict(zip(field_names, field_vals))

    def save_fields(self):
        """Save dictionary of input fields and values for faster upload later"""

        drop_down_options = dict(zip(['emitter', 'feed', 'propellant',
        'substrate_emitter', 'substrate_feed', 'field'],[self._emitter,
            self._feed, self._propellant, self._emitter_substrate,
            self._feed_substrate, self._field]))

        temp_dict = drop_down_options.copy()
        temp_dict.update(self._input_fields)

        fname = ('./input_field_files/' + self._emitter + '_and_' +
                self._feed + '_with_' + self._independent_variable +
                '.pickle')

        with open(fname, 'wb') as f:
            pickle.dump(temp_dict, f)

    def upload_data_individual(self):
        """Upload the data field by field"""

        for key, val in self._input_fields.items():
            temp = self.driver.find_element_by_name(key)
            if key not in ['emitter', 'feed', 'propellant', 'substrate_emitter',
                    'substrate_feed', 'field']:
                temp.clear()
                temp.send_keys(val)
            else:
                Select(temp).select_by_value(val)

    def upload_data_group(self):
        """Upload data using the upload config function on ESPET"""


    def run_sim(self):
        """Click the run button"""

        self.driver.find_element_by_id('runButton').click()

    def save_sim(self):
        """Save the simulation data and create pandas object"""

        self.driver.find_element_by_name('Save Data').click()

        s = 'output_data/' + self._emitter + ' and ' + self._feed + '.csv'

        self.sim_data= pd.read_csv(s)
        time.sleep(0.05)
        os.remove(s)

    @property
    def emitter(self):
        return self._emitter

    @emitter.setter
    def emitter(self, value):
        if np.issubdtype(type(value), np.string_) and value in self.__emitters:
            self._emitter = value
        elif np.issubdtype(type(value), np.int64) and value < len(self.__emitters):
            self._emitter = self.__emitters[value]
        else:
            raise TypeError('Emitter type must be string or int.')

    @property
    def feed(self):
        return self._feed

    @feed.setter
    def feed(self, value):
        if np.issubdtype(type(value), np.string_) and value in self.__feeds:
            self._feed= value
        elif np.issubdtype(type(value), np.int64) and value < len(self.__feeds):
            self._feed= self.__feeds[value]
        else:
            raise TypeError('Feed type must be string or int.')

    @property
    def propellant(self):
        return self._propellant

    @propellant.setter
    def propellant(self, value):
        if np.issubdtype(type(value), np.string_) and value in self.__propellants:
            self._propellant = value
        elif np.issubdtype(type(value), np.int64) and value < len(self.__propellants):
            self._propellant = self.__propellants[value]
        else:
            raise TypeError('Propellant type must be string or int.')

    @property
    def independent_variable(self):
        return self._independent_variable

    @independent_variable.setter
    def independent_variable(self, value):
        if np.issubdtype(type(value), np.string_) and value in self.__independent_variables:
            self._independent_variable = value
        elif np.issubdtype(type(value), np.int64) and value < len(self.__independent_variables):
            self._independent_variable = self.__independent_variabls[value]
        else:
            raise TypeError('Independent variable type must be string or int.')

    @property
    def emitter_substrate(self):
        return self._emitter_substrate

    @emitter_substrate.setter
    def emitter_substrate(self, value):
        if np.issubdtype(type(value), np.string_) and value in self.__emitter_substrates:
            self._emitter_substrate = value
        elif np.issubdtype(type(value), np.int64) and value < len(self.__emitter_substrates):
            self._emitter_substrate = self.__emitter_substrates[value]
        else:
            raise TypeError('Emitter substrate type must be string or int.')

    @property
    def feed_substrate(self):
        return self._feed_substrate

    @feed_substrate.setter
    def feed_substrate(self, value):
        if np.issubdtype(type(value), np.string_) and value in self.__feed_substrates:
            self._feed_substrate = value
        elif np.issubdtype(type(value), np.int64) and value < len(self.__feed_substrates):
            self._feed_substrate = self.__feed_substrates[value]
        else:
            raise TypeError('Feed substrate type must be string or int.')

    @property
    def field(self):
        return self._field

    @field.setter
    def field(self, value):
        if np.issubdtype(type(value), np.string_) and value in self.__fields:
            self._field = value
        elif np.issubdtype(type(value), np.int64) and value < len(self.__fields):
            self._field= self.__fields[value]
        else:
            raise TypeError('Field type must be string or int.')
