# Vox Machina  
_An IoT platform for monitoring machine noise_  
**by Team BattleBorn Blender**
- LB Corney
- Brian Worthington
- Richard J

Benefits
--------
To be edited by fork

Features
--------
To be edited by fork

Components
----------
To be edited by fork

Telemetry API
-------------
Devices:    
<table>
<thead><td>Asset</td><td>Device ID</td></thead>
<tr><td>Blow Dryer</td><td></td></tr>
<tr><td>Blender</td><td></td></tr>
<tr><td></td><td></td></tr>
</table>   
Blender: 

Methods:  
**GET**  
https://voxmachina.herokuapp.com/telemetry/<device_id>

**PUT**  
https://voxmachina.herokuapp.com/telemetry/<device_id>  
<table>
<thead><td>Field</td><td>Datatype</td><td>Required</td></thead>  
<tr><td>"fft":</td><td>[ 0.0 ]</td><td>yes</td></tr>
<tr><td>"temp":</td><td>0.0</td><td>yes</td></tr>  
<tr><td>"dt":</td><td>d0.0</td><td></td></tr>  
<tr><td>"location":</td><td>""</td><td></td></tr>  
<tr><td>"lat":</td><td>0.0</td><td></td></tr>  
<tr><td>"lon":</td><td>0.0</td><td></td></tr>   
</table>

 


Flask Bot References
--------------------
[README-UPSTREAM.md](https://bitbucket.org/collectiveacuity/flaskbotfork/src/master/README-UPSTREAM.md)  