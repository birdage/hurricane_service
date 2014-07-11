#!/usr/bin/python
"""WSGI server example"""
from __future__ import print_function
from gevent.pywsgi import WSGIServer
from shapely.geometry import Polygon,Point
import netCDF4
import datetime
import ast
import json

year = "year"
bbox = "bbox"

rec_year = "all"
rec_bbox = Polygon ((89 0, 89 -35, 26 -35, 26 0, 89 0))

class HurService():
    def __init__(self):
        self.startup()

    def startup(self):  
        print('Serving on 8088...')
        WSGIServer(('', 8088), self.application).serve_forever()

    def application(self,env, start_response):
        return_string = ''
        print (env['PATH_INFO'])
        if env['PATH_INFO'] == '/':
            start_response('404 Not Found', [('Content-Type', 'application/json')])
            return_string = '<h1>Not Found</h1>'
        elif  env['PATH_INFO'] =="/favicon.ico":
            start_response('404 Not Found', [('Content-Type', 'application/json')])
            return_string = '<h1>Not Found</h1>'   
            return 
        else:

            request = (env['PATH_INFO'])
            request = request[1:-1]
            
            split_request = request.split("&")
            if len(split_request) > 1:
                query_params = {}
                for param in split_request:
                    param_request = param.split("=")                  
                    query_params[param_request[0]] = param_request[1]
            
                start_response('200 OK', [('Content-Type', 'application/json')])
                return_string = self.open_dataset(query_params["year"])             
                return [return_string]
            
            else:
                start_response('404 Not Found', [('Content-Type', 'application/json')])
                return_string = '<h1>Not Found</h1>'    
                return [return_string]

       
        
    def open_dataset(self,year):
        dap_url = "./Allstorms.ibtracs_wmo.v03r05.nc"
        nc = netCDF4.Dataset(dap_url, 'r')
        lat = nc.variables['lat_wmo']  
        lon = nc.variables['lon_wmo']  
        obs = nc.variables['numObs']  

        #days since 1858-11-17 00:00:00
        time = nc.variables['time_wmo']
        ref_dt = datetime.datetime(1858, 11, 17, 0, 0, 0)  
        
        track = nc.variables['track_type']  
        storm = nc.variables['storm_sn']  
        name = nc.variables['name'] 
        wind = nc.variables['wind_wmo'] 
        pressure = nc.variables['pres_wmo'] 
        alt = nc.variables['alt'] 
        
        ignore_list = ['NOT NAMED','UNNAMED','NAMELESS']
        count = 0
        valid_indicies = []
        s_year = year

        resp_string = dict()
        for i in range(0,len(name)):
            storm_name = "".join(name[i])
            if storm_name in ignore_list:
                #ignore
                pass
            elif "UNNAMED" in storm_name:
                #ignore
                pass
            else:
                #its not got a weird name 
                if year is None:
                    count +=1
                    valid_indicies.append(i)
                else:   
                    val = time[i][0]
                    s_time = ref_dt + datetime.timedelta(val,0)
                    if (s_time.year == s_year):                        
                        valid_indicies.append(i)
                        resp_string[storm_name.lower()] = {"lat":lat[i][0:obs[i]].data.tolist(),
                                                           "lon":lon[i][0:obs[i]].data.tolist(),
                                                           "wind":wind[i][0:obs[i]].data.tolist(),
                                                           "pressure":pressure[i][0:obs[i]].data.tolist()
                                                           }
                        count +=1

        return str(resp_string)