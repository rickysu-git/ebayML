#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 28 19:54:17 2020

@author: rickysu
"""

import pandas as pd
import re
import json

# Create header columns
dataframe = pd.read_csv("mlchallenge_set_2021.tsv",sep="\t",header=None)
dataframe.columns = ['category', 'primary_image_url', 'all_image_urls', 'attributes', 'index']


# Create new columns for each of the attribute keys
# i.e. "(Brand:Shimano,US Shoe Size (Men's):4.5,Modified Item:No,Style:Cycling)"
# will yield new columns 'Brand', 'US Shoe Size (Men's)', 'Modified Item', 'Style'


attributes = dataframe['attributes'].tolist()
dataframe_length = len(dataframe)

new_attributes_column = []
for index, a in enumerate(attributes):
    if index % 1000 == 0:
        print(index)
        
    attribute_dict = {}
    
    a = a.replace(",", ", ")                            # Add whitespace after each comma
    open_paren = a.find("(")        
    close_paren = a.rindex(")")
    a = a[open_paren+1:close_paren] + a[close_paren+1:] # Remove surrounding parentheses
    a = re.split(':+', a)                               # Split by one or more colons
    a = [re.split(',(?![^()]*\))',i) for i in a]        # Split by commas that are not within parentheses
    
    for i in range(len(a)):
        if i == 0:
            column = a[i][0].strip()
            continue
        
        next_column = a[i][-1].strip()
        if i == len(a)-1:
            values = a[i]
        else:
            values = a[i][:-1]
            
        values = ','.join([i.strip().replace("  "," ") for i in values])
        
        if column not in attribute_dict:
            attribute_dict[column] = []
        attribute_dict[column].append(values)
            
        column = next_column
    
    new_attributes_column.append(json.dumps(attribute_dict))

dataframe['attributes_parsed'] = new_attributes_column
dataframe = dataframe.drop(columns=['attributes'])
dataframe.to_csv("parsed_attributes.csv")



# Separate training and validation sets
dataframe = pd.read_csv("parsed_attributes.csv")

# Load validation labels
validation_labels = pd.read_csv("mlchallenge_set_validation.tsv",sep="\t",header=None)
validation_labels.columns = ['listing_index', 'cluster_index']
listing_indices = validation_labels['listing_index'].tolist()

# Create validation dataframe
in_validation = dataframe.index.isin(listing_indices)
validation_df = dataframe[in_validation]
validation_df.to_csv("validation.csv")

in_training = [not elem for elem in in_validation.tolist()]
training_df = dataframe[in_training]
training_df.to_csv("training.csv")