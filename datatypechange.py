
#After Extracting from the API the "CSV" is uploaded to arcgis pro then converted into 'XY table' 
# below data type change is used as a python tool and changed the data types"
import arcpy
import datetime

def script_tool(input_fc, old_field, new_field_type):
    try:
        arcpy.AddMessage(f"Input Feature Class: {input_fc}")
        arcpy.AddMessage(f"Old Field: {old_field}")
        arcpy.AddMessage(f"New Field Type: {new_field_type}")

       
        new_field = f"temp_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        arcpy.AddMessage(f"Generated New Field: {new_field}")

        try:
            arcpy.management.AddField(input_fc, new_field, new_field_type)
            arcpy.AddMessage("Added new field successfully.")
        except arcpy.ExecuteError as e:
            arcpy.AddError(f"Error adding new field: {e}")
            return


        try:
            with arcpy.da.UpdateCursor(input_fc, [old_field, new_field]) as cursor:
                for row in cursor:
                    if row[0] is not None:
                        # Type conversion
                        if new_field_type == "TEXT":
                        
                            if isinstance(row[0], float):
                                row[1] = "{:.0f}".format(row[0])
                            else:
                                row[1] = str(row[0])
                        elif new_field_type == "DOUBLE":
                            row[1] = float(row[0])
                        elif new_field_type == "LONG":
                            row[1] = int(row[0])
                        elif new_field_type == "DATE":
                            row[1] = row[0]  
                        else:
                            row[1] = row[0]
                    cursor.updateRow(row)  
            arcpy.AddMessage("Updated new field successfully.")
        except arcpy.ExecuteError as e:
            arcpy.AddError(f"Error updating new field: {e}")
            return


        try:
            arcpy.management.DeleteField(input_fc, old_field)
            arcpy.AddMessage("Deleted old field successfully.")
        except arcpy.ExecuteError as e:
            arcpy.AddError(f"Error deleting old field: {e}")
            return

        try:
            arcpy.management.AlterField(input_fc, new_field, old_field, old_field)
            arcpy.AddMessage("Renamed new field successfully.")
        except arcpy.ExecuteError as e:
            arcpy.AddError(f"Error renaming new field: {e}")
            return


        arcpy.AddMessage("Field updated and renamed successfully.")

    except Exception as e:
        arcpy.AddError(f"An error occurred: {e}")


if __name__ == '__main__':

    input_fc = arcpy.GetParameterAsText(0) 
    old_field = arcpy.GetParameterAsText(1)  
    new_field_type = arcpy.GetParameterAsText(2)  

  
    script_tool(input_fc, old_field, new_field_type)
