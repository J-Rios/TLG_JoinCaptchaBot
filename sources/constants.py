# -*- coding: utf-8 -*-

'''
Script:
    constants.py
Description:
    Constants values for join_captcha_bot.py.
Author:
    Jose Rios Rubio
Creation date:
    09/09/2018
Last modified date:
    07/10/2018
Version:
    1.1.0
'''

####################################################################################################

### Constants ###
CONST = {
    'TOKEN' : 'XXXXXXXXX:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX', # Bot Token (get it from @BotFather)
    'DATA_DIR' : './data', # Data directory path
    'CHATS_DIR' : './data/chats', # Chats directory path
    'CAPTCHAS_DIR' : './data/captchas', # Directory where create/generate temporary captchas images
    'F_CONF' : 'configs.json', # Chat configurations JSON files name
    'INIT_TITLE' : 'Unknown Chat', # Initial chat title at Bot start
    'INIT_LINK' : 'Unknown', # Initial chat link at Bot start
    'INIT_LANG' : 'EN', # Initial language at Bot start
    'INIT_ENABLE' : True, # Initial enable/disable status at Bot start
    'INIT_CAPTCHA_TIME_MIN' : 5, # Initial captcha solve time (in minutes)
    'T_DEL_MSG' : 5, # Default time (in mins) to remove self-destruct sent messages from the Bot
    'DEVELOPER' : '@JoseTLG', # Bot developer
    'REPOSITORY' : 'https://github.com/J-Rios/TLG_JoinCaptchaBot', # Bot code repository
    'DEV_PAYPAL' : 'https://www.paypal.me/josrios', # Developer Paypal address
    'DEV_BTC' : '3N9wf3FunR6YNXonquBeWammaBZVzTXTyR', # Developer Bitcoin address
    'VERSION' : '1.1.0' # Bot version
}

TEXT = {
    'EN' : {
        'START' : \
            'Hello, I am a Bot that send a captcha for each new user who join a group, and kick ' \
            'any of them that can\'t solve the captcha in a specified time. If one user try to ' \
            'join the group for 3 times and never solve the captcha, I will assume that the ' \
            '"user" is a Bot, and It will be ban.\n' \
            '\n' \
            'Remember to give me administration privileges to kick-ban users.' \
            '\n' \
            'Check /help command for more information about my usage.',

        'HELP' : \
            'Bot help:\n' \
            '————————————————\n' \
            '- I am a Bot that send a captcha for each new user who join a group, and kick any ' \
            'of them that can\'t solve the captcha in a specified time.\n' \
            '\n' \
            '- If one user try to join the group for 3 times and never can\'t solve the captcha, ' \
            'I will assume that the "user" is a Bot, and it will be ban.\n' \
            '\n' \
            '- You need to provide me Administration rights for kick users and remove messages.\n' \
            '\n' \
            '- To preserve a clean group, I auto-remove all messages related to me when captcha ' \
            ' is not solved and the user was kicked (after 5 minutes).\n' \
            '\n' \
            '- The time that new users have to solve the captcha is 5 minutes, but it can be ' \
            'configured using the command /time.\n' \
            '\n' \
            '- You can turn on or off the captcha protection using the commands /enable and ' \
            '/disable.\n' \
            '\n' \
            '- Configuration commands just can be used by group Administrators.\n' \
            '\n' \
            '- You can change the language that I speak, using the command /language.\n' \
            '\n' \
            '- Check /commands for get a list of all avaliable commands, and a short ' \
            'description of all of them.',

        'CMD_NOT_ALLOW' : \
            'Just an Admin can use this command',

        'LANG_CHANGE' : \
            'Language changed to english.',

        'LANG_SAME' : \
            'I am already in english.\n\nMay you want to say:\n/language es',

        'LANG_BAD_LANG' : \
            'Invalid language provided. The actual languages supported are english and spanish, ' \
            'change any of them using "en" or "es".\n' \
            '\n' \
            'Example:\n' \
            '/language en\n' \
            '/language es',

        'LANG_NOT_ARG' : \
            'The command needs a language to set (en - english, es - spanish).\n' \
            '\n' \
            'Example:\n' \
            '/language en\n' \
            '/language es',

        'TIME_CHANGE' : \
            'Time to resolve captcha successfully changed to {} minutes.',

        'TIME_NOT_NUM' : \
            'The provided time is not an integer number.',

        'TIME_NOT_ARG' : \
            'The command needs a time value to set (in minutes).\n' \
            '\n' \
            'Example:\n' \
            '/time 3\n' \
            '/time 5\n' \
            '/time 10',

        'NEW_USER_CAPTCHA_CAPTION' : \
            'Hello {}, welcome to {}, please send a message with the number that appear in this ' \
            'captcha to verify that you are a human. If you don\'t resolve the captcha in {} ' \
            'mins, you will be automatically kick from the group.',

        'CAPTHA_SOLVED' : \
            'Captcha solved, user verified. Welcome to the group {}.',

        'CAPTCHA_INCORRECT_0' : \
            'That is not the correct number. Try again...',

        'CAPTCHA_INCORRECT_1' : \
            'That is not the correct number. Check closely, the captcha has 4 numbers...',

        'NEW_USER_KICK' : \
            '{} has not completed the captcha in time. "User" was kicked.',

        'NEW_USER_KICK_NOT_RIGHTS' : \
            '{} has not completed the captcha in time. I try to kick the "User", but I ' \
            'don\'t have the administration rights for kick users in the group.',

        'NEW_USER_KICK_NOT_IN_CHAT' : \
            '{} has not completed the captcha in time. I try to kick the "User", but the ' \
            'user is not in the group (has left the group or has been kicked by an Admin).',

        'BOT_CANT_KICK' : \
            '{} has not completed the captcha in time. I try to kick the "User", but for ' \
            'some unexpected problem (maybe network/server related), I can\'t do it.',

        'CANT_DEL_MSG' : \
            'I try to delete this message, but I don\'t have the administration rights for ' \
            'remove messages that has not been sent by me.',

        'NEW_USER_BAN' : \
            'Warning: This is the third time that {} has tried to join the group and fail to ' \
            'resolve the captcha. "User" was ban. To let he enter again, an Admin has to ' \
            'manually remove the restrictions of this "user".',

        'NEW_USER_BAN_NOT_IN_CHAT' : \
            'Warning: This is the third time that {} has tried to join the group and fail to ' \
            'resolve the captcha. I try to ban the "User", but the user is not in the group ' \
            '(has left the group or has been kicked/banned by an Admin).',

        'NEW_USER_BAN_NOT_RIGHTS' : \
            'Warning: This is the third time that {} has tried to join the group and fail to ' \
            'resolve the captcha. I try to ban the "User", but I don\'t have the administration ' \
            'rights for ban users in the group.',

        'BOT_CANT_BAN' : \
            'Warning: This is the third time that {} has tried to join the group and fail to ' \
            'resolve the captcha. I try to ban the "User", but for some unexpected problem ' \
            '(maybe network/server related), I can\'t do it.',

        'OTHER_CAPTCHA_BTN_TEXT' : \
            'Other Captcha',

        'ENABLE' : \
            'Captcha protection enabled. Disable it with /disable command.',

        'DISABLE' : \
            'Captcha protection disabled. Enable it with /enable command.',

        'ALREADY_ENABLE' : \
            'The captcha protection is already enabled.',

        'ALREADY_DISABLE' : \
            'The captcha protection is already disabled.',

        'CAN_NOT_GET_ADMINS' : \
            'Can\'t use this command in the current chat.',

        'VERSION' : \
            'Actual Bot version: {}',

        'ABOUT_MSG' : \
            'This is an open-source GNU-GPL licensed Bot developed by the telegram user {}. You ' \
            'can check the code here:\n{}\n\n---------------------------------------------\n\n' \
            'Do you like my work? Buy me a coffee.\n\nPaypal:\n{}\n\nBTC:\n{}',
       
        'COMMANDS' : \
            'List of commands:\n' \
            '————————————————\n' \
            '/start - Show the initial information about the bot.\n' \
            '\n' \
            '/help - Show the help information.\n' \
            '\n' \
            '/commands - Show the actual message. Information about all the available commands ' \
            'and their description.\n' \
            '\n' \
            '/language - Allow to change the language of the bot messages. Actual available ' \
            'languages: en (english) - es (spanish).\n' \
            '\n' \
            '/enable - Enable the captcha protection of the group.\n' \
            '\n' \
            '/disable - Disable the captcha protection of the group.\n' \
            '\n' \
            '/version - Show the version of the Bot.\n' \
            '\n' \
            '/about - Show about info.'
    },
    'ES' : {
        'START' : \
            'Hola, soy un Bot que envia un captcha a cada nuevo usuario que se une al grupo, y ' \
            'kickeo a los que no resuelvan el captcha en un tiempo determinado. Si un usuario ' \
            'ha intentado unirse al grupo 3 veces y nunca resolvió el captcha, supondré que ese ' \
            '"usuario" es un Bot y lo banearé.\n' \
            '\n' \
            'Recuerda que para funcionar de forma adecuada debes darme permisos de ' \
            'administración para suspender usuarios en el grupo.\n' \
            '\n' \
            'Echa un vistazo al comando /help para conocer más información sobre mi uso.',

        'HELP' : \
            'Ayuda sobre el Bot:\n' \
            '————————————————\n' \
            '- Soy un Bot que envia un captcha a cada nuevo usuario que se une al grupo, y ' \
            'kickeo a los que no resuelvan el captcha en un tiempo determinado.\n' \
            '\n' \
            '- Si un usuario ha intentado unirse al grupo 3 veces y nunca resolvió el captcha, ' \
            'supondré que ese "usuario" es un Bot y lo banearé.\n' \
            '\n' \
            '- Debes darme permisos de Administración para suspender usuarios y eliminar ' \
            'mensajes.\n' \
            '\n' \
            '- Para mantener limpio el grupo, elimino aquellos mensajes que tengan relación ' \
            'conmigo cuando no se haya resuelto el captcha y el usuario haya sido kickeado ' \
            '(transcurridos 5 minutos).\n' \
            '\n' \
            '- El tiempo que disponen los usuarios para resolver el captcha son 5 minutos, pero ' \
            'este tiempo puede ser cambiado mediante el comando /time.\n' \
            '\n' \
            '- Puedes activar o desactivar la protección captcha mediante los comandos /enable y ' \
            '/disable.\n' \
            '\n' \
            '- Los comandos de configuraciones solo pueden ser usados por los Administradores ' \
            'del grupo.\n' \
            '\n' \
            '- Puedes cambiar el idioma en el que hablo mediante el comando /language.\n' \
            '\n' \
            '- Echa un vistazo al comando /commands para ver una lista con todos los comandos ' \
            'disponibles y una breve descripción de cada uno de ellos.',

        'CMD_NOT_ALLOW' : \
            'Solo un Admin puede utilizar este comando.',

        'LANG_CHANGE' : \
            'Idioma cambiado a español.',

        'LANG_SAME' : \
            'Ya estoy en español.\n\nQuizás querías decir:\n/language en',

        'LANG_BAD_LANG' : \
            'Idioma inválidado. Los idiomas actualmente soportados son el español y el inglés, ' \
            'cambia a uno de ellos mediante las etiquetas "es" o "en".\n' \
            '\n' \
            'Ejemplo:\n' \
            '/language es\n' \
            '/language en',

        'LANG_NOT_ARG' : \
            'El comando necesita un idioma que establecer (es - español, en - inglés).\n' \
            '\n' \
            'Ejemplo:\n' \
            '/language es\n' \
            '/language en',

        'TIME_CHANGE' : \
            'Tiempo para resolver el captcha cambiado a {} minutos.',

        'TIME_NOT_NUM' : \
            'El tiempo entregado no es un número entero.',

        'TIME_NOT_ARG' : \
            'El comando necesita un valor de tiempo a establecer (en minutos).\n' \
            '\n' \
            'Ejemplo:\n' \
            '/time 3\n' \
            '/time 5\n' \
            '/time 10',

        'NEW_USER_CAPTCHA_CAPTION' : \
            'Hola {}, bienvenido a {}, por favor envía un mensaje con el número que aparece ' \
            'en esta imagen para verificar que eres un humano. Si no resuelves este captcha en ' \
            '{} mins, serás kickeado del grupo automáticamente.',

        'CAPTHA_SOLVED' : \
            'Captcha resuelto, usuario verificado. Bienvenido al grupo {}.',

        'CAPTCHA_INCORRECT_0' : \
            'Ese no es el número correcto. Inténtalo nuevamente...',

        'CAPTCHA_INCORRECT_1' : \
            'Ese no es el número correcto. Fijate bien, el captcha tiene 4 numeros...',

        'NEW_USER_KICK' : \
            '{} no completó el captcha a tiempo. El "usuario" fue kickeado.',

       'NEW_USER_KICK_NOT_RIGHTS' : \
            '{} no completó el captcha a tiempo. El "usuario" debería ser kickeado, pero ' \
            'no se me han dado los privilegios de administración necesarios para expulsar ' \
            'usuarios del grupo.',

        'NEW_USER_KICK_NOT_IN_CHAT' : \
            '{} no completó el captcha a tiempo. Iba a kickear al "usuario", pero ya no ' \
            'se encuentra en el grupo (salió del grupo o fue kickeado/baneado por un Admin).',

        'BOT_CANT_KICK' : \
            '{} no completó el captcha a tiempo. He intentado kickear al "usuario", pero ' \
            'debido a un problema inesperado (quizás relacionado con la red o el servidor), no ' \
            'he podido hacerlo.',

        'CANT_DEL_MSG' : \
            'He intentado borrar este mensaje pero no se me han dado los privilegios de ' \
            'administración necesarios para eliminar mensajes que no son míos.',

        'NEW_USER_BAN' : \
            'Atención: Esta es la tercera vez que el usuario {} ha intentado unirse al grupo ' \
            'y no pudo resolver el captcha. El "usuario" fue baneado. Para permitir que intente ' \
            'entrar nuevamente al grupo, un Admin debe de quitar la restricción del usuario ' \
            'de forma manual en las opciones de administración del grupo.',

        'NEW_USER_BAN_NOT_IN_CHAT' : \
            'Atención: Esta es la tercera vez que el usuario {} ha intentado unirse al grupo ' \
            'y no pudo resolver el captcha. El "usuario" debería ser baneado, pero ya no se ' \
            'encuentra en el grupo (salió del grupo o fue kickeado/baneado por un Admin).',

        'NEW_USER_BAN_NOT_RIGHTS' : \
            'Atención: Esta es la tercera vez que el usuario {} ha intentado unirse al grupo ' \
            'y no pudo resolver el captcha. El "usuario" debería ser baneado, pero no se me han ' \
            'dado los privilegios de administración necesarios para expulsar usuarios del grupo.',

        'BOT_CANT_BAN' : \
            'Atención: Esta es la tercera vez que el usuario {} ha intentado unirse al grupo ' \
            'y no pudo resolver el captcha. El "usuario" debería ser baneado, pero debido a un ' \
            'problema inesperado (quizás relacionado con la red o el servidor), no he podido ' \
            'hacerlo.',

        'OTHER_CAPTCHA_BTN_TEXT' : \
            'Otro Captcha',

        'ENABLE' : \
            'Protección captcha activada. Desactívala con el comando /disable.',

        'DISABLE' : \
            'Protección captcha desactivada. Actívala con el comando /enable.',

        'ALREADY_ENABLE' : \
            'La protección captcha ya está activada.',

        'ALREADY_DISABLE' : \
            'La protección captcha ya está desactivada.',

        'CAN_NOT_GET_ADMINS' : \
            'No se puede usar este comando en el chat actual.',

        'VERSION' : \
            'Versión actual del Bot: {}',

        'ABOUT_MSG' : \
            'Este es un Bot open-source con licencia GNU-GPL, desarrollado por el usuario de ' \
            'telegram {}. Puedes consultar el código aquí:\n{}\n\n' \
            '---------------------------------------------\n\nTe gusta lo que hago? ' \
            'Invítame a un café.\n\nPaypal:\n{}\n\nBTC:\n{}',

        'COMMANDS' : \
            'Lista de comandos:\n' \
            '————————————————\n' \
            '/start - Muestra la información inicial sobre el Bot.\n' \
            '\n' \
            '/help - Muestra la información de ayuda.\n' \
            '\n' \
            '/commands - Muestra el mensaje actual. Información sobre todos los comandos ' \
            'disponibles y su descripción.\n' \
            '\n' \
            '/language - Permite cambiar el idioma en el que habla el Bot. Idiomas actualmente ' \
            'disponibles: es (español) - en (inglés).\n' \
            '\n' \
            '/enable - Activa la protección captcha en el grupo.\n' \
            '\n' \
            '/disable - Desactiva la protección captcha en el grupo.\n' \
            '\n' \
            '/version - Consulta la versión del Bot.\n' \
            '\n' \
            '/about - Muestra la información \"acerca de...\" del Bot.'
    }
}
