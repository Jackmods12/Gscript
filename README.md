# Gscript

**Examples will be coming shortly :)**

A scripting language made for a upcoming project to build a operating system ontop of the linux kernal to act more like windows than linux

* Fully Wrote in python
* Python 3.5+ Needed

| Version Name | Version Number | Date |
|----|-----|-------| 
| GScript 1 | 0.1.0 | ? |
| GScript 1X | 0.1.5 | ? |
| GScript 2 | 0.2.0 | ? |
| GScript 2X | ? | Still in the works |

## How to run a GS file
```
gscript filename
```

## How to install a GScript
```
Window:
  Right Click install.py and Run As Administrator
Linux:
  Open terminal in the folder where install.py is the run "sudo python3 install.py"
```

# Basic Syntax

```
func new set($a)
  loop
    print "Text"
    if $a == 1 then
      print "True"
    endif
    else
      print "False"
    endelse
  endloop
endfunc

func new run(1)
```

## Read and write to file

```
$a = "Lol"
filewrite "append" "Hey" $a
fileread "Hey" $b

print $b
```

## Http Get and Post

```
httpGET "https://pastebin.com/raw/YbvZHGYP" $b
httpPOST "https://pastebin.com/raw/YbvZHGYP" "Baby" $b

print $b
```
