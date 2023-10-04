# Import .Net runtime support - needs "pip install pythonnet"
import clr

# Get Geo SCADA Library (could use the namespace if the dll is on PATH)
CS = clr.AddReference( "c:\Program Files\Schneider Electric\ClearSCADA\ClearSCADA.Client.dll" )
import ClearScada.Client as CSClient 


# Create node and connect, then log in. (Could read net parameters from SYSTEMS.XML)
node = CSClient.ServerNode( CSClient.ConnectionType.Standard, "127.0.0.1", 5481 )
connection = CSClient.Simple.Connection( "Utility" )
connection.Connect( node )
connection.LogOn( "Username", "Password" )

# Function Converts the Group from an InstanceTemplate to a Generic Group
def convert_to_group(connection, obj):
    try:
        obj_type = obj.GetProperty("TypeName")
        print(f"Visiting: {obj.FullName}, Type: {obj_type}")

        if obj_type == 'CTemplateInstance':
            try:
                obj.Convert("CGroup")
                print(f"Converted {obj.FullName}")
            except Exception as e:
                print(f"Conversion Failed: {str(e)}")
        
        # Check number of children and type
        children = obj.GetChildren("", "")
        print(f"Found {len(children)} children for {obj.FullName}")

        for child in children:
            child_type = child.GetProperty("TypeName")
            if child_type in ['CTemplateInstance', 'CGroup']:
                convert_to_group(connection, child)

    except Exception as e:
        print(f"An error occurred: {str(e)}")


# Get the root object from where the recursion should start
try:
    root_obj = connection.GetObject("Water.Yarrambat Res.WQD614 - Fernhill")
except Exception as e:
    print(f"Failed to get the object: {str(e)}")
    exit()

# Perform conversion
convert_to_group(connection, root_obj)

def convert_points(connection, obj):
    try:
        obj_type = obj.GetProperty("TypeName")
        print(f"Visiting: {obj.FullName}, Type: {obj_type}")

        # Map of object types to convert from and to
        conversion_map = {
            'CeNETAnalogIn': 'CDNP3AnalogIn',
            'CeNETAnalogOut': 'CDNP3AnalogOut',
            'CeNETBinaryIn': 'CDNP3BinaryIn',
            'CeNETBinaryOut': 'CDNP3BinaryOut',
			'CeNETPulseNull': 'CDNP3BinaryOut'
        }
        
        # If object type matches any type for conversion, perform conversion
        if obj_type in conversion_map:
            try:
                obj.Convert(conversion_map[obj_type])
                print(f"Converted: {obj.FullName} to {conversion_map[obj_type]}")
            except Exception as e:
                print(f"Failed to convert {obj.FullName}: {str(e)}")
        
        # For objects of type CGroup, get children and process them
        if obj_type == 'CGroup':
            children = obj.GetChildren("", "")
            for child in children:
                convert_points(connection, child)

    except Exception as e:
        print(f"Error encountered: {str(e)}")

# Get the root object
root_obj = connection.GetObject("Water.Yarrambat Res.WQD614 - Fernhill")

# Execute conversion
convert_points(connection, root_obj)

