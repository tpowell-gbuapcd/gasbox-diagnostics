#!/usr/bin/env python3

# list of functions needed to plot the data from the remote gas sensors
# currently building this script with functions to work with the newly acquired gas sensors that
# will be integrated into both units. The current script on the raspberry pi is smarter and should
# recognize what sensors are connected and what are not.

import time, os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import argparse
import logging

from datetime import date, datetime, timedelta


def reader(file_path):
    '''
    Reads CSV as a pandas datafreame and returns it for plotting

    input param: file_path, the file containing the 10 minute averages of diagnostic data for one day. 
    input type: string
    
    output param: df, pandas dataframe containing the data from file.
    output type: pandas, dataframe
    '''

    df = pd.read_csv(file_path, header=0)
    
    return df


def get_file(date, plat):
    '''
    Returns the name of the CSV file of 10-minute averages.    

    input param: date, the date of data we want to plot
    input type: string
        
    input param: plat, the platform where the data we want to plot are from
    input type: string
    
    output param: file_name, yesterdays csv file of the 10-minute average data for plotting
    output type: string
    '''
    
    return plat + date[0:2] + date[3:5] + date [6:10] + '.csv' 
  

def get_date(arg):
    '''
    Return the date of the file that we're plotting/making the text file for. If no argument is given, then the 
    date we want is the current day. If an argument is given, then we simply return the argument.

    input param: arg, the date that is passed as an argument to the script running in the crontab
    input type: string
    '''  

    if arg == None:
        return_date = date.today().strftime('%m-%d-%Y') 
    else:
        return_date = arg

    return return_date 
    

def set_directory(directory, date, plat):
    '''
    Set the save directory of plot and text/csv files. Directories are broken up by day.

    input param: directory, the path to the directory of data.
    input type: string

    input param: date, the date of data we want to plot
    input type: string

    input param: plat, the platform where the data we want to plot are from

    return param: day_dir, directory for plots with name of the format dd-mm-yyy.
    '''
    
    print(directory, date, plat)
    day_dir = directory + date + '/'
    
    if not os.path.exists(day_dir):
        os.makedirs(day_dir)
    
    #logging.info('Average Data Text Files Saved to {}'.format(avg_day_dir))
    #logging.info('Plots Saved to {}'.format(plot_day_dir))

    return day_dir


def make_text(file_name, save_directory, frame):
    '''
    Create a more easily readable text file of the data from the raspberry pi. Also calculate the total 
    current and power draw of the device. 

    input param: file_name, the csv file name with data we want to parse into a more easily read text file. 
    input type: string

    input param: save_directory, where the more easily readable text file will be saved
    input type: string

    input param: frame, the pandas dataframe containing our data
    input type: pandas dataframe
    '''
    text_file = file_name[:-4] + '.txt'

    header = ''

    try:
        # since the file is so small (~80kB at most) just rewrite the whole file each time a new line 
        # appears in the csv
        # this isn't the best way to do this, could probably append new lines to the end of the file
        with open(save_directory+text_file, 'w') as txt:
            for val in list(frame.columns):

                if val == 'Time':
                    header += '{:<25}'.format(val)
                else:
                    header += '{:<20}'.format(val)

            header += '{:<20}{:<20}'.format('Total Current', 'Total Power')
            txt.write(header+'\n')

            for index, row in frame.iterrows():

                str_vals = ''
                current_tot = 0
                power_tot = 0

                for val, ind in zip(row.values, row.index):

                    #Calculate total power and current draw
                    if 'Current' in ind:
                        current_tot += val
                    if 'Power' in ind:
                        power_tot += val

                    # if the value is the date, the format is different
                    if type(val) is str:
                        str_vals += '{:<25}'.format(val)
                    else:
                        str_vals += '{:<20.2f}'.format(val)

                str_vals += '{:<20.2f}{:<20.2f}\n'.format(current_tot, power_tot)
                txt.write(str_vals)
            txt.close()

    except Exception as e:
        print(e)
        logging.error('Error Encountered: {}'.format(e), exc_info=True)


def get_plot_params(cols):
    '''
    Create a tuple using zip that has the data to be plotted and the plot number they go on. Also, return the number of subplots needed    

    input param: cols, a list of all of the keys of the pandas dataframe
    input type: list

    output param: plot_params, tuple of lists that has the type of plotted data [PM, Current, etc] with the plot number.
    output type: tuple
    ouput param: plot_count, the number of subplots needed to display the data
    output type: integer
    '''
    
    plot_count = 0
    counted_list = []
    plot_num = []    

    try:    
        for val in cols:
            print(val)
            if 'PM' in val:
                if 'PM' not in counted_list:
                    counted_list.append('PM')
                    plot_count += 1
                    plot_num.append(plot_count)
            if 'Temp' or 'RH' in val:
                if 'Temp' not in counted_list:
                    counted_list.append('Temp')
                    plot_count += 1
                    plot_num.append(plot_count)
                if 'RH' not in counted_list:
                    counted_list.append('RH')
                    plot_num.append(plot_count)
            if 'Current' in val:
                if 'Current' not in counted_list:
                    counted_list.append('Current')
                    plot_count += 1
                    plot_num.append(plot_count)
            if 'Voltage' in val:
                if 'Voltage' not in counted_list:
                    counted_list.append('Voltage')
                    plot_count += 1
                    plot_num.append(plot_count)
            if 'Power' in val:
                if 'Power' not in counted_list:
                    counted_list.append('Power')
                    plot_count += 1
                    plot_num.append(plot_count)
            if 'Pressure' in val:
                if 'Pressure' not in counted_list:
                    counted_list.append('Pressure')
                    plot_count += 1
                    plot_num.append(plot_count)
            if 'Gas' or 'CO2' in val:
                if 'Gas' not in counted_list:
                    counted_list.append('Gas')
                    plot_count += 1
                    plot_num.append(plot_count)
                if 'CO2' not in counted_list:
                    counted_list.append('CO2')
                    plot_num.append(plot_count)

        #print(counted_list, plot_num, plot_count)
        
        plot_params = zip(counted_list, plot_num)
        #print(list(plot_params))

    except Exception as e:
        print(e)
        logging.error('Error Encounted: {}'.format(e), exc_info=True)

    return plot_count, plot_params  


def plot_data(frame, save_directory, plat, file_name, date):
    '''
    Plot the data from file

    input param: frame, pandas data frame containing all the data from the csv file
    input type: pandas dataframe

    input param: save_directory, the directory where the plot will be saved
    input type: string 

    input param: plat, platform we are plotting data for
    input type: string

    input param: file_name, the name of the csv file we're plotting from. Will share names but be different type
    input type: string
    
    input param: date
    input type: string
    '''
    
    number_of_plots, plot_parameters = get_plot_params(list(frame.columns))
    plot_names, plot_nums = zip(*plot_parameters)

    plot_file = file_name[:-4] + '.png'
    lg_size = 6
    
    #print(number_of_plots, list(plot_parameters))
    print(plot_names, plot_nums)
  
    fig, ax = plt.subplots(number_of_plots, sharex=True, figsize=(10, 15))

    '''
    #prints the key needed to access the data in the frame, and the data
    for val in list(frame.columns):
        print(val, frame[val])
    '''

    # these are used to make sure colors aren't duplicated in the temperature and RH plots
    hot_colors = ['r', '#F97306', 'm', '#FFFF14']
    cold_colors = ['b', 'g', 'c']
    h_i = 0
    c_i = 0

    # used for correctly applying handles in temp and rh plots
    temp_rh_handles = []    
    gas_handles = []

    # make sure the frames are in ascending order according to Time
    # this can be hard coded since we will alwasy have a Time frame and it will always be called Time
    frame = frame.sort_values('Time', ascending=True)
    try:
        for val in list(frame.columns):
            print(val)
            if 'PM' in val:
                if 'ST' in val:
                    next
                else:
                    pm_ind = plot_nums[plot_names.index('PM')]-1
                    ax[pm_ind].plot(frame['Time'], frame[val], label=val)
                    #ax[pm_ind].set_ylim(bottom=0)
                    ax[pm_ind].set_ylabel('PM Conc (ug/m3)')
                    ax[pm_ind].grid(True)
                    ax[pm_ind].legend(loc='upper left', prop={'size':lg_size})
                    ax[pm_ind].xaxis.set_major_locator(plt.LinearLocator(12))

            if 'Current' in val:
                curr_ind = plot_nums[plot_names.index('Current')]-1
                ax[curr_ind].plot(frame['Time'], frame[val], label=val)
                ax[curr_ind].set_ylim(0,500)
                ax[curr_ind].set_ylabel('Current (mA)')
                ax[curr_ind].grid(True)
                ax[curr_ind].legend(loc='upper left', prop={'size':lg_size})
                ax[curr_ind].xaxis.set_major_locator(plt.LinearLocator(12))

            if 'Power' in val:
                pow_ind = plot_nums[plot_names.index('Power')]-1
                ax[pow_ind].plot(frame['Time'], frame[val], label=val)
                ax[pow_ind].set_ylim(0, 15)
                ax[pow_ind].set_ylabel('Power (W)')
                ax[pow_ind].grid(True)
                ax[pow_ind].legend(loc='upper left', prop={'size':lg_size})
                ax[pow_ind].xaxis.set_major_locator(plt.LinearLocator(12))

            if 'Voltage' in val:
                volt_ind = plot_nums[plot_names.index('Voltage')]-1
                ax[volt_ind].plot(frame['Time'], frame[val], label=val)
                ax[volt_ind].set_ylim(0, 16)
                ax[volt_ind].set_ylabel('Voltage (V)')
                ax[volt_ind].grid(True)
                ax[volt_ind].legend(loc='upper left', prop={'size':lg_size})
                ax[volt_ind].xaxis.set_major_locator(plt.LinearLocator(12))
            if 'Temp' or 'RH' in val:
                #these if/else statements allow us to us both temp and rh, or just one of them.
                if 'Temp' and 'RH' in plot_names:
                    temp_ind = plot_nums[plot_names.index('Temp')]-1
                    rh_ind = plot_nums[plot_names.index('RH')]-1

                    if temp_ind > rh_ind:
                        if 'Temp' in val:
                            lg, = ax[temp_ind].plot(frame['Time'], frame[val], label=val, c=hot_colors[h_i])
                            temp_rh_handles.append(lg)
                            h_i += 1
                            ax[temp_ind].grid(True)
                            ax[temp_ind].set_ylim(-20, 80)
                            ax[temp_ind].set_ylabel("Temp (C))")
                            ax[temp_ind].set_xlim(frame['Time'].iloc[0], frame['Time'].iloc[-1])
                            ax[temp_ind].legend(handles=temp_rh_handles, loc='upper right', prop={'size':lg_size})

                        if 'RH' in val:
                            rh_ax = ax[temp_ind].twinx()
                            rh_ind = plot_nums[plot_names.index('RH')]
                            lg, = rh_ax.plot(frame['Time'], frame[val], label=val, c=cold_colors[c_i])
                            temp_rh_handles.append(lg)
                            c_i += 1
                            #rh_ax.grid(True)
                            rh_ax.set_ylim(0, 100)
                            rh_ax.set_ylabel("RH (%)")
                            ax[temp_ind].legend(handles=temp_rh_handles, loc='upper right', prop={'size':lg_size})
                            
                    else:
                        if 'RH' in val:
                            lg, = ax[rh_ind].plot(frame['Time'], frame[val], label=val, c=cold_colors[c_i])
                            temp_rh_handles.append(lg)
                            c_i += 1
                            ax[rh_ind].grid(True)
                            ax[rh_ind].set_ylim(0,100)
                            ax[rh_ind].set_ylabel("RH (%))")
                            ax[rh_ind].set_xlim(frame['Time'].iloc[0], frame['Time'].iloc[-1])
                            ax[rh_ind].legend(handles=temp_rh_handles, loc='upper right', prop={'size':lg_size})

                        if 'Temp' in val:
                            temp_ax = ax[rh_ind].twinx()
                            lg, = temp_ax.plot(frame['Time'], frame[val], label=val, c=hot_colors[h_i])
                            temp_rh_handles.append(lg)
                            h_i += 1
                            #temp_ax.grid(True)
                            temp_ax.set_ylim(-20, 80)
                            temp_ax.set_ylabel("Temp (C)")
                            ax[rh_ind].legend(handles=temp_rh_handles, loc='upper right', prop={'size':lg_size})

                elif 'Temp' in list(frame.columns) and 'RH' not in plot_names:
                    if 'Temp' in val:
                        temp_ind = plot_nums[plot_names.index('Temp')]-1
                        ax[temp_ind].plot(frame['Time'], frame[val], label=val, c=hot_colors[h_i])
                        h_i += 1
                        ax[temp_ind].grid(True)
                        ax[temp_ind].set_ylim(-20, 80)
                        ax[temp_ind].set_ylabel("Temp (C))")
                        ax[temp_ind].set_xlim(frame['Time'].iloc[0], frame['Time'].iloc[-1])
                        ax[temp_ind].legend(handles=temp_rh_handles, loc='upper right', prop={'size':lg_size})
                elif 'RH' in list(frame.columns) and 'Temp' not in plot_names:
                    if 'RH' in val:
                        rh_ind = plot_nums[plot_names.index('RH')]-1
                        ax[rh_ind].plot(frame['Time'], frame[val], label=val, c=cold_colors[c_i])
                        c_i += 1
                        ax[rh_ind].grid(True)
                        ax[rh_ind].set_ylim(0,100)
                        ax[rh_ind].set_ylabel("RH (%))")
                        ax[rh_ind].set_xlim(frame['Time'].iloc[0], frame['Time'].iloc[-1])
                        ax[rh_ind].legend(handles=temp_rh_handles, loc='upper right', prop={'size':lg_size})


            if 'Pressure' in val:
                press_ind = plot_nums[plot_names.index('Pressure')]-1
                ax[press_ind].plot(frame['Time'], frame[val], label=val)
                ax[press_ind].set_ylim(0, 1000)
                ax[press_ind].set_ylabel('Pressure (hPa)')
                ax[press_ind].grid(True)
                ax[press_ind].legend(loc='upper left', prop={'size':lg_size})
                ax[press_ind].xaxis.set_major_locator(plt.LinearLocator(12))

            if 'Gas' or 'CO2' in val:
                #check to see that both exist in the list
                #if they do, evaluate where the are in the list to know which axes to create first
                if 'Gas' and 'CO2' in plot_names:
                    gas_ind = plot_nums[plot_names.index('Gas')]-1
                    co2_ind = plot_nums[plot_names.index('CO2')]-1
                    
                    if gas_ind > co2_ind:
                        if 'Gas' in val:
                            #gas_ind = plot_nums[plot_names.index('Gas')]
                            lg, = ax[gas_ind].plot(frame['Time'], frame[val], label=val, c='r')
                            gas_handles.append(lg)
                            ax[gas_ind].grid(True)
                            ax[gas_ind].set_ylim(bottom=0)
                            ax[gas_ind].set_ylabel("BME Gas (ohms)")
                            ax[gas_ind].set_xlim(frame['Time'].iloc[0], frame['Time'].iloc[-1])
                            ax[gas_ind].legend(handles=gas_handles, loc='upper right', prop={'size':lg_size})

                        if 'CO2' in val:
                            co2_ax = ax[gas_ind].twinx()
                            lg, = co2_ax.plot(frame['Time'], frame[val], label=val, c='b')
                            gas_handles.append(lg)
                            #co2_ax.grid(True)                     
                            co2_ax.set_ylim(bottom=0)                   
                            co2_ax.set_ylabel("CO2 CONC (PPM)")
                            ax[gas_ind].legend(handles=gas_handles, loc='upper right', prop={'size':lg_size})
                    else:
                        if 'CO2' in val:
                            lg, = ax[co2_ind].plot(frame['Time'], frame[val], label=val, c='b')
                            gas_handles.append(lg)
                            ax[co2_ind].grid(True)
                            ax[co2_ind].set_ylim(bottom=0)
                            ax[co2_ind].set_ylabel("CO2 CONC (PPM)")
                            ax[co2_ind].set_xlim(frame['Time'].iloc[0], frame['Time'].iloc[-1])
                            ax[co2_ind].legend(handles=gas_handles, loc='upper right', prop={'size':lg_size})
                        if 'Gas' in val:
                            gas_ax = ax[co2_ind].twinx()
                            lg, = gas_ax.plot(frame['Time'], frame[val], label=val, c='r')
                            gas_handles.append(lg)
                            #gas_ax.grid(True)
                            gas_ax.set_ylim(bottom=0)
                            gas_ax.set_ylabel("BME Gas (ohms)")
                            ax[co2_ind].legend(handles=gas_handles, loc='upper right', prop={'size':lg_size})


                elif ('Gas' in plot_names and 'CO2' not in plot_names):
                    if 'Gas' in val:
                        gas_ind = plot_nums[plot_names.index('Gas')]-1
                        ax[gas_ind].plot(frame['Time'], frame[val], label=val, c='r')     
                        ax[gas_ind].grid(True)
                        ax[gas_ind].set_ylim(bottom=0)
                        ax[gas_ind].set_ylabel("BME Gas (ohms)")
                        ax[gas_ind].set_xlim(frame['Time'].iloc[0], frame['Time'].iloc[-1])
                        ax[gas_ind].legend(handles=gas_handles, loc='upper right', prop={'size':lg_size})

                elif ('CO2' in plot_names and 'Gas' not in plot_names):
                    print("eff")
                    if 'CO2' in val:
                        co2_ind = plot_nums[plot_names.index('CO2')]-1
                        ax[co2_ind].plot(frame['Time'], frame[val], label=val, c='b')
                        ax[co2_ind].grid(True)
                        ax[co2_ind].set_ylim(bottom=0)
                        ax[co2_ind].set_ylabel("CO2 CONC (PPM)")
                        ax[co2_ind].set_xlim(frame['Time'].iloc[0], frame['Time'].iloc[-1])
                        ax[co2_ind].legend(handles=gas_handles, loc='upper right', prop={'size':lg_size})

        
        ax[0].set_xlim(frame['Time'].iloc[0], frame['Time'].iloc[-1])
        ax[0].xaxis.set_major_locator(plt.LinearLocator(12))  
        plt.xticks(rotation=35)
        plot_name = save_directory + plot_file
        print(plot_name)
        fig.suptitle(plat + "Data From " + date)
        plt.gcf().autofmt_xdate()
        #plt.set_loglevel('ERROR')
        plt.tight_layout()
        plt.savefig(plot_name, dpi=300)
        plt.close()
        
    except Exception as e:
        print(e)
        logging.error('Error Encountered: {}'.format(e), exc_info=True)


