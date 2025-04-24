"""
Data Export Module
Supports exporting weather data in multiple formats
"""
import json
import csv
import xml.dom.minidom as md
import xml.etree.ElementTree as ET
import os
from datetime import datetime

class DataExporter:
    """Data export class, supports multiple format data exports"""
    
    @staticmethod
    def export_to_json(data, file_path=None):
        """Export data to JSON format
        
        Args:
            data: Data to be exported
            file_path: Export file path, returns string if None
            
        Returns:
            str: Returns JSON string if file_path is None; otherwise returns None
        """
        json_data = json.dumps(data, ensure_ascii=False, indent=4)
        
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(json_data)
            return None
        else:
            return json_data
    
    @staticmethod
    def export_to_csv(data, file_path=None, headers=None):
        """Export data to CSV format
        
        Args:
            data: Data to be exported (list of dictionaries)
            file_path: Export file path, returns string if None
            headers: Column headers, if None uses data keys
            
        Returns:
            str: Returns CSV string if file_path is None; otherwise returns None
        """
        if not data:
            return "" if file_path is None else None
            
        if headers is None and isinstance(data[0], dict):
            headers = list(data[0].keys())
        
        csv_data = []
        if headers:
            csv_data.append(','.join(headers))
        
        for item in data:
            if isinstance(item, dict):
                row = [str(item.get(h, '')) for h in headers]
            else:
                row = [str(i) for i in item]
            csv_data.append(','.join(row))
        
        csv_string = '\n'.join(csv_data)
        
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(csv_string)
            return None
        else:
            return csv_string
    
    @staticmethod
    def export_to_xml(data, root_name='data', item_name='item', file_path=None):
        """Export data to XML format
        
        Args:
            data: Data to be exported
            root_name: XML root element name
            item_name: Data item element name
            file_path: Export file path, returns string if None
            
        Returns:
            str: Returns XML string if file_path is None; otherwise returns None
        """
        root = ET.Element(root_name)
        
        if isinstance(data, list):
            for item in data:
                item_elem = ET.SubElement(root, item_name)
                if isinstance(item, dict):
                    for key, value in item.items():
                        if value is not None:
                            child = ET.SubElement(item_elem, key)
                            child.text = str(value)
        elif isinstance(data, dict):
            for key, value in data.items():
                if value is not None:
                    child = ET.SubElement(root, key)
                    child.text = str(value)
        
        xml_string = ET.tostring(root, encoding='utf-8').decode('utf-8')
        dom = md.parseString(xml_string)
        pretty_xml = dom.toprettyxml(indent="  ")
        
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(pretty_xml)
            return None
        else:
            return pretty_xml
    
    @staticmethod
    def export_to_markdown(data, title="Weather Data Report", file_path=None):
        """Export data to Markdown format
        
        Args:
            data: Data to be exported
            title: Document title
            file_path: Export file path, returns string if None
            
        Returns:
            str: Returns Markdown string if file_path is None; otherwise returns None
        """
        md_lines = [f"# {title}", "", f"Generated Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ""]
        
        if isinstance(data, list):
            # If list data, create table
            if data and isinstance(data[0], dict):
                headers = list(data[0].keys())
                md_lines.append("| " + " | ".join(headers) + " |")
                md_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
                
                for item in data:
                    row = [str(item.get(h, '')) for h in headers]
                    md_lines.append("| " + " | ".join(row) + " |")
            else:
                md_lines.append("## Data Items")
                for i, item in enumerate(data):
                    md_lines.append(f"{i+1}. {item}")
        elif isinstance(data, dict):
            # If dictionary data, create list
            md_lines.append("## Data Details")
            for key, value in data.items():
                md_lines.append(f"- **{key}**: {value}")
        
        md_string = "\n".join(md_lines)
        
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(md_string)
            return None
        else:
            return md_string
    
    @staticmethod
    def export_weather_data(data, format_type, file_path=None):
        """Export weather data in specified format
        
        Args:
            data: Weather data to be exported
            format_type: Export format (json, csv, xml, markdown)
            file_path: Export file path, returns string if None
            
        Returns:
            str: Returns formatted string if file_path is None; otherwise returns None
        """
        if format_type.lower() == 'json':
            return DataExporter.export_to_json(data, file_path)
        elif format_type.lower() == 'csv':
            return DataExporter.export_to_csv(data, file_path)
        elif format_type.lower() == 'xml':
            return DataExporter.export_to_xml(data, 'weather_data', 'record', file_path)
        elif format_type.lower() == 'markdown' or format_type.lower() == 'md':
            return DataExporter.export_to_markdown(data, "Weather Data Report", file_path)
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
