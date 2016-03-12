import os
import sublime
import sublime_plugin

class RunappCommand(sublime_plugin.WindowCommand):
    def stvers(self):
        # Last stable release Mac build number
        # may need adjustment for other platforms. 
        vers = None
        if int(sublime.version()) <= 2221:
            vers = 2
        else:
            vers = 3
        return vers

    def run(self, app = "", args = [], type = "" , macopen = "default"):
        vers = self.stvers()

        # get the string of $FILE$
        file_s = self.window.active_view().file_name()

        # get the string of $DIR$
        dir_s = os.path.split(file_s)[0]

        # get the string of $PROJ$
        # ST2 has no ptoject data
        proj_s = None
        if vers >= 3 :
            data = sublime.active_window().project_data()
        else:
            data = None
        if data != None:
            for folder in data['folders']:
                proj_s = folder['path']
                break

        # handle the 'type'
        if type == "file":
            target = '"'+file_s+'"'
        elif type == "dir":
            target = '"'+dir_s+'"'
        elif type == "proj":
            if proj_s != None:
                target = '"'+proj_s+'"'
            else:
                sublime.error_message('It\'s not a project yet. Please go to "Project->Save Project as..." firstly.')
                return

        # handle the embedded $var$
        elif type == "none":
            target = ""
            for i in range(0,len(args)):
                arg = args[i]
                arg = arg.replace('$FILE$', '"'+file_s+'"')
                arg = arg.replace('$DIR$', '"'+dir_s+'"')
                if proj_s != None:
                    arg = arg.replace('$PROJ$', '"'+proj_s+'"')
                args[i] = arg

        else:
            sublime.error_message('"type" must be one of "file", "dir", "proj", and "none".')

        if target is None:
            return

        # invoke the application
        # import subprocess
        try:
            # join to one string for os.popen
            # ? subprocess.Popen can't work with msys_git 2.5.3
            exec_s = ' '.join(['"'+app+'"'] + args + [target])
            # print(exec_s)
            args_s = ' '.join( args + [target])
            # print (args_s)
            if sublime.platform() == 'osx':
                if macopen == "unix":
                    # Just like windows and linux, use when you want to specify 
                    # a command line program.
                    os.popen(exec_s)
                elif macopen == "open":
                    # Assume thet the open(1) command will work
                    # and ignore the specified app
                    os.popen('open ' + args_s)
                elif macopen == "plumb":
                    # If you have the Plan 9 from Userspace plumbing installed
                    # let the plumbing file figure it out and ignore the
                    # specified app
                    # os.popen('open -a Plumb.app ' + args_s)
                    # The above method for plumb has issues with file names with spaces.
                    # If the install is via homebrew, this should work.
                    #os.popen('/usr/local/bin/9 plumb ' + args_s)
                    print("Run Apps: Plumb option not currently supported")
                else:
                    # subprocess.Popen(['open', '-a', app] + args + [target])
                    os.popen('open -a ' + exec_s)
            else:
                # subprocess.Popen([app] + args + [target])
                os.popen(exec_s)
        except:
            sublime.error_message('Unable to open current file with "' + app + '", check the Console.')

    def is_enabled(self):
        return True

class AddappCommand(sublime_plugin.WindowCommand):
    def run(self):
        vers = self.stvers()
        # print 'VERSION' , vers , sublime.version()
        cmdFile = os.path.join(sublime.packages_path(), 'User', 'Run App.sublime-commands')
        if not os.path.isfile(cmdFile):
            # os.makedirs(cmdFile, 0o775)
            content = """[
    {
        "caption": "Run: Git",
        "command": "runapp",
        "args":{
            "app": "D:\\\\Tools\\\\Git\\\\git-bash.exe",
            "args": ["--cd=$DIR$"],
            "type": "none"
        }

    },

    {
        "caption": "Run: Chrome",
        "command": "runapp",
        "args":{
            "app": "C:\\\\Program Files\\\\Google\\\\Chrome\\\\Application\\\\chrome.exe",
            "args": [],
            "type": "file"
        }

    },
    {
        "caption": "Open: Mac Open",  // Open file with open(1) on OSX
        "command": "runapp",
        "args":{
          // application full path on Win/Linux, or only name on MAC
          // ignored with macopen:"open"
          "app": "", 

          // argument list
          // variables can be use: $DIR$, $FILE$, $PROJ$
          "args": ["$FILE$"],

          // define what should follow the command:
          // "dir" - file directory, same as $DIR$
          // "file" - file name, same as $FILE$
          // "proj" - project directory, same as $PROJ$
          // "none" - nothing: if args use variables, "type" must be "none"
          "type": "none",
          "macopen" : "open"
        }
    }

]"""

            if vers == 3:
                open(cmdFile, 'w+', encoding='utf8', newline='').write(str(content))
            else:
                open(cmdFile, 'w+').write(str(content))
        sublime.active_window().open_file(cmdFile)

    def is_enabled(self):
        return True