# Vox Machina  
_An IoT platform for monitoring machine noise_  
**by Team BattleBorn Blender**
- LB Corney
- Brian Worthington
- Richard J

![Architecture](https://github.com/rj919/voxmachina/raw/master/VoxMachinaDiagram.png)

Telemetry API
-------------
Devices:    
<table>
<thead><td>Asset</td><td>Device ID</td></thead>
<tr><td><b>Blow Dryer</b></td><td>sDuYkEJ4-RpjEDqLLMpJUkyV</td></tr>
<tr><td><b>Blender</b></td><td>NR2ZJOI0iq5E95bYPd35KlHn</td></tr>
<tr><td></td><td></td></tr>
</table>

Methods:  
**GET**  
https://voxmachina.herokuapp.com/telemetry/<device_id>

**PUT**  
https://voxmachina.herokuapp.com/telemetry/<device_id>  
<table>
<thead><td>Field</td><td>Datatype</td><td>Required</td></thead>  
<tr><td><b>fft</b></td><td>[ 0.0 ]</td><td>yes</td></tr>
<tr><td><b>temp</b></td><td>0.0</td><td></td></tr>  
<tr><td><b>dt</b></td><td>0.0</td><td></td></tr>  
<tr><td><b>location</b></td><td>""</td><td></td></tr>  
<tr><td><b>lat</b></td><td>0.0</td><td></td></tr>  
<tr><td><b>lon</b></td><td>0.0</td><td></td></tr>   
</table>

**Note**: [ 0.0 ] means an array of numbers
 


Flask Bot References
--------------------
[README-UPSTREAM.md](https://bitbucket.org/collectiveacuity/flaskbotfork/src/master/README-UPSTREAM.md)  