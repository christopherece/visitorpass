from flask import Flask, request, jsonify
import sys
import traceback
import brother_ql
from brother_ql.backends import backend_factory
from brother_ql import BrotherQLRaster, create_label
from brother_ql.conversion import convert
import socket
import os

app = Flask(__name__)

def get_brother_printers():
    """Get available Brother QL-700 printers"""
    printers = []
    try:
        # Try to find USB printers
        import usb.core
        
        # Brother QL-700 USB Vendor ID: 0x04f9
        # Brother QL-700 USB Product ID: 0x2057
        devices = usb.core.find(find_all=True, 
                              idVendor=0x04f9,  # Brother vendor ID
                              idProduct=0x2057)  # QL-700 product ID
                              
        if devices:
            for device in devices:
                try:
                    # Get device details
                    port = f"/dev/usb/lp{device.address}"
                    printers.append({
                        'name': 'Brother QL-700',
                        'port': port,
                        'type': 'brother_ql'
                    })
                    print(f"Found Brother QL-700 at port: {port}")
                    print(f"Device details: {device}")
                except Exception as e:
                    print(f"Error processing device: {str(e)}")
        else:
            print("No Brother QL-700 printers found")
            
    except Exception as e:
        print(f"Error finding printers: {str(e)}")
    return printers

def print_brother_label(data, printer_port):
    """Print label using Brother QL-700"""
    try:
        from brother_ql.raster import BrotherQLRaster
        from brother_ql.backends import backend_factory
        from PIL import Image, ImageDraw, ImageFont
        
        # Create label raster object
        qlr = BrotherQLRaster('QL-700')
        
        # Create a simple text label
        # Create a blank image
        img = Image.new('1', (300, 100), 'white')  # 300 pixels wide, 100 pixels tall
        draw = ImageDraw.Draw(img)
        
        # Use a simple font
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        # Draw the text
        draw.text((10, 10), data, font=font, fill='black')
        
        # Convert image to printer format
        # Instead of using brother_ql's conversion, we'll use a simple binary format
        pixels = img.load()
        width, height = img.size
        label_data = []
        
        for y in range(height):
            row = []
            for x in range(width):
                row.append(255 if pixels[x, y] else 0)
            label_data.append(row)
        
        # Get the USB backend
        backend_class = backend_factory('pyusb')
        if backend_class is None:
            raise Exception("USB backend not available")
            
        # Create a backend instance
        backend = backend_class()
        
        # Connect to printer
        backend.connect(printer_port)
        if not backend.is_connected:
            raise Exception(f"Could not connect to printer at {printer_port}")
            
        # Send the label to printer
        # Send initialization commands
        backend.write(b'\x1B\x40')  # Initialize printer
        backend.write(b'\x1D\x21\x00')  # Set default print settings
        
        # Send the label data
        for row in label_data:
            backend.write(bytes(row))
        
        # Cut the label
        backend.write(b'\x1D\x56\x01')  # Cut label
        
        backend.dispose()
        return True
    except Exception as e:
        print(f"Error printing: {str(e)}")
        return False

def get_printer_status(printer_port):
    """Get printer status"""
    try:
        # Get the USB backend
        backend_class = backend_factory('pyusb')
        if backend_class is None:
            return {
                'status': 'error',
                'error': 'USB backend not available'
            }
            
        # Create a backend instance
        backend = backend_class()
        
        # Connect to printer
        backend.connect(printer_port)
        if backend.is_connected:
            return {
                'status': 'online',
                'port': printer_port
            }
        else:
            return {
                'status': 'offline',
                'port': printer_port
            }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }

@app.route('/printers', methods=['GET'])
def list_printers():
    try:
        brother_printers = get_brother_printers()
        return jsonify({
            'printers': brother_printers,
            'count': len(brother_printers)
        })
    except Exception as e:
        print(f"Error getting printers: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/print', methods=['POST'])
def print_label():
    try:
        # Get JSON data from request
        data = request.json
        
        # Get printer information
        printer_port = data.get('printer_port')
        if not printer_port:
            return jsonify({"error": "No printer port specified"}), 400
            
        # Print label
        success = print_brother_label(data.get('content', ''), printer_port)
        if success:
            return jsonify({"status": "success", "message": "Label printed successfully"})
        else:
            return jsonify({"status": "error", "message": "Failed to print label"}), 500
    except Exception as e:
        error_msg = str(e)
        print(f"\n=== Print Error ===")
        print(f"Error: {error_msg}")
        print(f"Full traceback: {traceback.format_exc()}")
        return jsonify({"error": error_msg}), 500

@app.route('/status', methods=['GET'])
def printer_status():
    try:
        printer_port = request.args.get('printer_port')
        if not printer_port:
            return jsonify({"error": "No printer port specified"}), 400
            
        status = get_printer_status(printer_port)
        return jsonify(status)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting Print Service...")
    print(f"Python version: {sys.version}")
    print(f"System version: {os.uname()}")
    
    # List available printers at startup
    brother_printers = get_brother_printers()
    print("\n=== Available Brother QL-700 Printers ===")
    for printer in brother_printers:
        print(f"Name: {printer['name']}")
        print(f"Port: {printer['port']}")
        print("-" * 40)
    
    # Ensure Flask runs on all interfaces
    print(f"Starting Flask server on 0.0.0.0:8001")
    print(f"Available at: http://192.168.10.57:8001")
    
    app.run(
        host='0.0.0.0',  # Listen on all interfaces
        port=8001,
        debug=True,
        threaded=True  # Allow multiple requests
    )
