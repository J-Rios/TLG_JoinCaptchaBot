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
    10/06/2019
Version:
    1.4.1
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
    'INIT_CAPTCHA_DIFFICULTY_LEVEL' : 2, # Initial captcha difficult level
    'INIT_CAPTCHA_CHARS_MODE' : "nums", # Initial captcha characters mode (nums, hex or ascci)
    'T_DEL_MSG' : 5, # Default time (in mins) to remove self-destruct sent messages from the Bot
    'F_TLDS' : 'tlds-alpha-by-domain.txt', # IANA TLD list (https://data.iana.org/TLD/tlds-alpha-by-domain.txt)
    'REGEX_URLS' : r'((?<=[^a-zA-Z0-9])*(?:https\:\/\/|[a-zA-Z0-9]{{1,}}\.{{1}}|\b)(?:\w{{1,}}\.{{1}}){{1,5}}(?:{})\b/?(?!@))',
    'DEVELOPER' : '@JoseTLG', # Bot developer
    'REPOSITORY' : 'https://github.com/J-Rios/TLG_JoinCaptchaBot', # Bot code repository
    'DEV_PAYPAL' : 'https://www.paypal.me/josrios', # Developer Paypal address
    'DEV_BTC' : '3N9wf3FunR6YNXonquBeWammaBZVzTXTyR', # Developer Bitcoin address
    'VERSION' : '1.4.1 (10/06/2019)' # Bot version
}

TEXT = {
    'EN' : {
        'START' : \
            'Hello, I am a Bot that send an image captcha for each new user who join a group, ' \
            'and kick anyone that can\'t solve the captcha in a specified time.\n' \
            '\n' \
            'If one user try to join the group for 3 times and never solve the captcha, I will ' \
            'assume that this "user" is a Bot, and It will be ban. Also, any message that ' \
            'contains an URL sent by a new "user" before captcha completion, will be considered ' \
            'Spam and will be deleted.\n' \
            '\n' \
            'Remember to give me administration privileges to kick-ban users and remove ' \
            'messages.\n' \
            '\n' \
            'Check /help command for more information about my usage.\n' \
            '\n' \
            'Am I useful? Check /about command and consider to make a donation to keep me active.',

        'HELP' : \
            'Bot help:\n' \
            '————————————————\n' \
            '- I am a Bot that send a captcha for each new user who join a group, and kick any ' \
            'of them that can\'t solve the captcha in a specified time.\n' \
            '\n' \
            '- If one user try to join the group for 3 times and never can\'t solve the captcha, ' \
            'I will assume that the "user" is a Bot, and it will be ban.\n' \
            '\n' \
            '- Any message that contains an URL that has been sent by a new "user" before ' \
            'captcha completion, will be considered Spam and will be deleted.\n' \
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
            '- You can configure captcha difficulty level using command /difficulty.\n' \
            '\n' \
            '- You can set captcha to use just numbers (default) or full numbers and letters, ' \
            'using command /change_mode.\n' \
            '\n' \
            '- Check /commands for get a list of all avaliable commands, and a short ' \
            'description of all of them.',

        'CMD_NOT_ALLOW' : \
            'Just an Admin can use this command',

        'LANG_CHANGE' : \
            'Language changed to english.',

        'LANG_SAME' : \
            'I am already in english.\n' \
            '\n' \
            'May you want to say:\n' \
            '/language es\n' \
            '/language ca\n' \
            '/language pt_br',

        'LANG_BAD_LANG' : \
            'Invalid language provided. The actual languages supported are english, spanish, ' \
            'catalan and portuguese (Brazil). Change any of them using "en", "es", "ca" or ' \
            '"pt_br".\n' \
            '\n' \
            'Example:\n' \
            '/language en\n' \
            '/language es\n' \
            '/language ca\n' \
            '/language pt_br',

        'LANG_NOT_ARG' : \
            'The command needs a language to set (en - english, es - spanish, ' \
            'ca - catalan, pt_br - portugese from Brazil).\n' \
            '\n' \
            'Example:\n' \
            '/language en\n' \
            '/language es\n' \
            '/language ca\n' \
            '/language pt_br',

        'TIME_CHANGE' : \
            'Time to resolve captcha successfully changed to {} minutes.',

        'TIME_MAX_NOT_ALLOW' : \
            'Maximum captcha solve time is 120 minutes. Time not changed.',

        'TIME_NOT_NUM' : \
            'The provided time is not an integer number.',

        'TIME_NOT_ARG' : \
            'The command needs a time value to set (in minutes).\n' \
            '\n' \
            'Example:\n' \
            '/time 3\n' \
            '/time 5\n' \
            '/time 10',

        'DIFFICULTY_CHANGE' : \
            'Captchas difficulty successfully changed to level {}.',

        'DIFFICULTY_NOT_NUM' : \
            'The provided captchas difficulty is not a number.',

        'DIFFICULTY_NOT_ARG' : \
            'The command needs a difficulty level to set (from 1 to 5).\n' \
            '\n' \
            'Example:\n' \
            '/difficulty 1\n' \
            '/difficulty 2\n' \
            '/difficulty 3\n' \
            '/difficulty 4\n' \
            '/difficulty 5',

        'CAPTCHA_MODE_CHANGE' : \
            'Captchas character-mode successfully changed to "{}".',

        'CAPTCHA_MODE_INVALID' : \
            'Invalid captcha character-mode. Supported modes are: "nums", "hex" and "ascii".\n' \
            '\n' \
            'Example:\n' \
            '/captcha_mode nums\n' \
            '/captcha_mode hex\n' \
            '/captcha_mode ascii',

        'CAPTCHA_MODE_NOT_ARG' : \
            'The command needs a characters mode to set. Availables modes are:\n' \
            '- Numeric Captchas ("nums").\n' \
            '- Hexadecimal Captchas, numbers and characters A-F ("hex").\n' \
            '- Numbers and characters A-Z Captchas (ascii").\n' \
            '\n' \
            'Example:\n' \
            '/captcha_mode nums\n' \
            '/captcha_mode hex\n' \
            '/captcha_mode ascii',

        'NEW_USER_CAPTCHA_CAPTION' : \
            'Hello {}, welcome to {}, please send a message with the number that appear in this ' \
            'captcha to verify that you are a human. If you don\'t resolve the captcha in {} ' \
            'mins, you will be automatically kick from the group.',

        'CAPTHA_SOLVED' : \
            'Captcha solved, user verified.\nWelcome to the group {}',

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

        'SPAM_DETECTED_RM' : \
            'Detected a message with an URL (or an alias) from {}, who has not solved the ' \
            'captcha yet. The message has been removed for the sake of a Telegram free of Spam :)',

        'SPAM_DETECTED_NOT_RM' : \
            'Message with an URL (or an alias) detected from {}, who has not solved the captcha ' \
            'yet. I try to remove the Spam message, but I don\'t have the administration rights ' \
            'for remove messages that has not been sent by me.',

        'NOT_TEXT_MSG_ALLOWED' : \
            'Removed a non-text message (image, audio, file...) from {}, for the sake of a ' \
            'Telegram free of Spam.\n' \
            '\n' \
            'You can send non-text messages after you have resolved the captcha.',

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
            'This is a free software and open-source GNU-GPL licensed Bot developed by {}.\n' \
            '\n' \
            'You can check the code here:\n' \
            '{}\n' \
            '\n' \
            'Do you like my work? Buy me a coffee.\n' \
            '\n' \
            'Paypal:\n' \
            '{}\n' \
            '\n' \
            'BTC:\n' \
            '{}',
       
        'COMMANDS' : \
            'List of commands:\n' \
            '————————————————\n' \
            '/start - Shows the initial information about the bot.\n' \
            '\n' \
            '/help - Shows the help information.\n' \
            '\n' \
            '/commands - Shows the actual message. Information about all the available commands ' \
            'and their description.\n' \
            '\n' \
            '/language - Allows to change the language of the bot messages. Actual available ' \
            'languages: en (english) - es (spanish) - pt_br (portuguese from Brazil).\n' \
            '\n' \
            '/time - Allows to change the time available to resolve a captcha.\n' \
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
            'Hola, soy un Bot que envia una imagen captcha a cada nuevo usuario que se une al ' \
            'grupo, y kickeo a los que no resuelvan el captcha en un tiempo determinado.\n' \
            '\n' \
            'Si un usuario ha intentado unirse al grupo 3 veces y nunca resolvió el captcha, ' \
            'supondré que ese "usuario" es un Bot y lo banearé. Además, cualquier mensaje que ' \
            'contenga una URL y haya sido enviado por un nuevo "usuario" antes de que este haya ' \
            'resuelto el captcha, será considerado un mensaje de Spam y será borrado.\n' \
            '\n' \
            'Recuerda que para funcionar de forma adecuada debes darme permisos de ' \
            'administración para suspender usuarios y eliminar mensajes del grupo.\n' \
            '\n' \
            'Echa un vistazo al comando /help para conocer más información sobre mi uso.\n' \
            '\n' \
            'Soy útil? Echa un vistazo al comando /about y considera hacer una donación para ' \
            'mantenerme activo.',

        'HELP' : \
            'Ayuda sobre el Bot:\n' \
            '————————————————\n' \
            '- Soy un Bot que envia un captcha a cada nuevo usuario que se une al grupo, y ' \
            'kickeo a los que no resuelvan el captcha en un tiempo determinado.\n' \
            '\n' \
            '- Si un usuario ha intentado unirse al grupo 3 veces y nunca resolvió el captcha, ' \
            'supondré que ese "usuario" es un Bot y lo banearé.\n' \
            '\n' \
            '- Cualquier mensaje que contenga una URL y haya sido enviado por un nuevo "usuario" ' \
            'antes de que este haya resuelto el captcha, será considerado un mensaje de Spam y ' \
            'será borrado.\n' \
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
            '- Puedes configurar el nivel de dificultad del captcha mediante el comando ' \
            '/difficulty.\n' \
            '\n' \
            '- Puedes establecer que los captchas solo contengan números (por defecto), o ' \
            'números y letras, a través del comando /change_mode.\n' \
            '\n' \
            '- Echa un vistazo al comando /commands para ver una lista con todos los comandos ' \
            'disponibles y una breve descripción de cada uno de ellos.',

        'CMD_NOT_ALLOW' : \
            'Solo un Admin puede utilizar este comando.',

        'LANG_CHANGE' : \
            'Idioma cambiado a español.',

        'LANG_SAME' : \
            'Ya estoy en español.\n' \
            '\n' \
            'Quizás querías decir:\n' \
            '/language en\n' \
            '/language ca\n' \
            '/language pt_br',

        'LANG_BAD_LANG' : \
            'Idioma inválidado. Los idiomas actualmente soportados son el inglés, el español, ' \
            'el catalán y el portugués de Brasil. Cambia a uno de ellos mediante las etiquetas ' \
            '"en", "es", "ca" o "pt_br".\n' \
            '\n' \
            'Ejemplo:\n' \
            '/language en\n' \
            '/language es\n' \
            '/language ca\n' \
            '/language pt_br',

        'LANG_NOT_ARG' : \
            'El comando necesita un idioma que establecer (en - inglés, es - español, ' \
            'ca - catalán, pt_br - portugués de Brasil).\n' \
            '\n' \
            'Ejemplo:\n' \
            '/language en\n' \
            '/language es\n' \
            '/language ca\n' \
            '/language pt_br',

        'TIME_CHANGE' : \
            'Tiempo para resolver el captcha cambiado a {} minutos.',

        'TIME_MAX_NOT_ALLOW' : \
            'El tiempo máximo para resolver el captcha son 120 minutos. No se cambió el tiempo.',

        'TIME_NOT_NUM' : \
            'El tiempo entregado no es un número entero.',

        'TIME_NOT_ARG' : \
            'El comando necesita un valor de tiempo a establecer (en minutos).\n' \
            '\n' \
            'Ejemplo:\n' \
            '/time 3\n' \
            '/time 5\n' \
            '/time 10',

        'DIFFICULTY_CHANGE' : \
            'Nivel de dificultad de los captchas cambiado a {}.',

        'DIFFICULTY_NOT_NUM' : \
            'El nivel de dificultad proporcionado no es un número.',

        'DIFFICULTY_NOT_ARG' : \
            'El comando necesita un nivel de dificultad a establecer (de 1 a 5).\n' \
            '\n' \
            'Ejemplo:\n' \
            '/difficulty 1\n' \
            '/difficulty 2\n' \
            '/difficulty 3\n' \
            '/difficulty 4\n' \
            '/difficulty 5',

        'CAPTCHA_MODE_CHANGE' : \
            'Modo-caracter de los capcthas cambiado a "{}".',

        'CAPTCHA_MODE_INVALID' : \
            'Modo-caracter invalido. Los modos disponibles son: "nums", "hex" y "ascii".\n' \
            '\n' \
            'Ejemplo:\n' \
            '/captcha_mode nums\n' \
            '/captcha_mode hex\n' \
            '/captcha_mode ascii',

        'CAPTCHA_MODE_NOT_ARG' : \
            'El comando necesita el modo-caracter a establecer. Los modos disponibles son:\n' \
            '- Captchas numéricos ("nums").\n' \
            '- Captchas hexadecimales, con números y letras A-F ("hex").\n' \
            '- Captchas con números y letras A-Z (ascii").\n' \
            '\n' \
            'Ejemplo:\n' \
            '/captcha_mode nums\n' \
            '/captcha_mode hex\n' \
            '/captcha_mode ascii',

        'NEW_USER_CAPTCHA_CAPTION' : \
            'Hola {}, bienvenido a {}, por favor envía un mensaje con el número que aparece ' \
            'en esta imagen para verificar que eres un humano. Si no resuelves este captcha en ' \
            '{} mins, serás kickeado del grupo automáticamente.',

        'CAPTHA_SOLVED' : \
            'Captcha resuelto, usuario verificado.\nBienvenido al grupo {}',

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

        'SPAM_DETECTED_RM' : \
            'Se ha detectado un mensaje que contiene una URL (o alias) enviado por {}, quien aún ' \
            'no ha resuelto el captcha. El mensaje ha sido eliminado en aras de un Telegram ' \
            'libre de Spam :)',

        'SPAM_DETECTED_NOT_RM' : \
            'Se ha detectado un mensaje con URL (o alias) enviado por {}, quien aún no ha ' \
            'resuelto el captcha. He intentado borrar el mensaje, pero no se me han dado los ' \
            'privilegios de administración necesarios para eliminar mensajes que no son míos.',

        'NOT_TEXT_MSG_ALLOWED' : \
            'Eliminado un mensaje que no es de texto (imagen, audio, archivo...) enviado por {}, ' \
            'en aras de un Telegram libre de Spam.\n' \
            '\n' \
            'Podrás enviar mensajes que no sean de texto una vez que hayas resuelto el captcha.',

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
            'Este es un Bot de software libre open-source con licencia GNU-GPL, desarrollado por ' \
            '{}.\n' \
            '\n' \
            'Puedes consultar el código aquí:\n' \
            '{}\n' \
            '\n' \
            'Te gusta lo que hago? Invítame a un café.\n' \
            '\n' \
            'Paypal:\n' \
            '{}\n' \
            '\n' \
            'BTC:\n' \
            '{}',

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
            'disponibles: es (español) - en (inglés) - pt_br (portugués de Brasil).\n' \
            '\n' \
            '/time - Permite cambiar el tiempo disponible para resolver un captcha.\n' \
            '\n' \
            '/enable - Activa la protección captcha en el grupo.\n' \
            '\n' \
            '/disable - Desactiva la protección captcha en el grupo.\n' \
            '\n' \
            '/version - Consulta la versión del Bot.\n' \
            '\n' \
            '/about - Muestra la información \"acerca de...\" del Bot.'
    },
    'CA' : {
        'START':
            'Hola, sóc un Bot que envia una imatge captcha a cada nou usuari que s\'uneixi al ' \
            'grup, i kickejo als que no resolguin el captcha en un temps determinat.\n' \
            '\n' \
            'Si un usuari ha intentat unir-se al grup 3 vegades i mai ha resolt el captcha, ' \
            'suposaré que aquell "usuari" és un Bot i el banejaré. A més, qualsevol missatge ' \
            'que contingui una URL i hagi estat enviat per un nou "usuari" abans que aquest ' \
            'hagi resolt el captcha, serà considerat un missatge d\'Spam i serà esborrat.\n' \
            '\n' \
            'Recorda que per a funcionar de forma adequada has de donar-me permisos ' \
            'd\'administració per a suspendre usuaris i eliminar missatges del grup.\n' \
            '\n' \
            'Dóna un cop d\'ull al comandament /help per a conèixer més informació sobre el meu ' \
            'ús.\n' \
            '\n' \
            'Sóc útil? Dóna un cop d\'ull al comandament /about i considereu que feu una donació ' \
            'per mantenir-me actiu.',

        'HELP':
            'Ajuda sobre el Bot:\n' \
            '————————————————\n' \
            '- Sóc un Bot que envia un captcha a cada nou usuari que s\'uneix al grup, i kickejo ' \
            'qui no resolgui el captcha en un temps determinat.\n' \
            '\n' \
            '- Si un usuari ha intentat unir-se al grup 3 vegades i mai ha resolt el captcha, ' \
            'suposaré que aquell "usuari" és un Bot i el banejaré.\n' \
            '\n' \
            '- Qualsevol missatge que contingui una URL i hagi estat enviat per un nou "usuari" ' \
            'abans que aquest hagi resolt el captcha, serà considerat un missatge d\'Spam i serà ' \
            'esborrat.\n' \
            '\n' \
            '- Has de donar-me permisos d\'Administració per a suspendre usuaris i eliminar ' \
            'missatges.\n' \
            '\n' \
            '- Per tal de mantenir net el grup, elimino aquells missatges que tinguin relació ' \
            'amb mi quan no s\'hagi resolt el captcha i l\'usuari hagi estat kickejat ' \
            '(transcorreguts 5 minuts).\n' \
            '\n' \
            '- El temps del que disposen els usuaris per a resoldre el captcha són 5 minuts, ' \
            'però aquest temps es pot canviar mitjançant el comandament /time.\n' \
            '\n' \
            '- Pots activar o desactivar la protecció captcha mitjançant els comandaments ' \
            '/enable i /disable.\n' \
            '\n' \
            '- Els comandaments de configuracions només poden ser utilitzats per els ' \
            'Administradors del grup.\n' \
            '\n' \
            '- Pots canviar l\'idioma en el que parlo mitjançant el comandament /language.\n' \
            '\n' \
            '- Pots configurar el nivell de dificultat del captcha mitjançant la comanda ' \
            '/difficulty.\n' \
            '\n' \
            'Pots establir que els captchas només continguin números (per defecte), ' \
            'o números i lletres, a través de la comanda /captcha_mode.\n' \
            '\n' \
            '- Dóna un cop d\'ull al comandament /commands per a veure una llista amb tots els ' \
            'comandaments disponibles i una breu descripció de cada un.',

        'CMD_NOT_ALLOW':
            'Només un Admin pot utiltzar aquest comandament.',

        'LANG_CHANGE':
            'Idioma canviat a català.',

        'LANG_SAME':
            'Ja estic en català.\n' \
            '\n' \
            'Potser volies dir:\n' \
            '/language en\n' \
            '/language es\n' \
            '/language pt_br',

        'LANG_BAD_LANG':
            'Idioma invalidat. Els idiomes actualment suportats són l\'anglès, el castellà, el ' \
            'català i el portuguès de Brasil. Canvia a un d\'ells mitjançant les etiquetes "en", ' \
            '"es", "ca", o "pt_br".\n' \
            '\n' \
            'Exemple:\n' \
            '/language en\n' \
            '/language es\n' \
            '/language ca\n' \
            '/language pt_br',

        'LANG_NOT_ARG':
            'El comandament necessita un idioma a establir (en - anglès, es - castellà, ' \
            'ca - català, pt_br - portuguès de Brasil)\n' \
            '\n' \
            'Exemple:\n' \
            '/language en\n' \
            '/language es\n' \
            '/language ca\n' \
            '/language pt_br',

        'TIME_CHANGE':
            'Temps per a resoldre el captcha canviat a {} minuts.',

        'TIME_MAX_NOT_ALLOW':
            'El temps màxim per a resoldre el captcha són 120 minuts. No s\'ha canviat el temps.',

        'TIME_NOT_NUM':
            'El temps entregat no és un número enter.',

        'TIME_NOT_ARG':
            'El comandament necessita un valor de temps a establir (en minuts).\n' \
            '\n' \
            'Exemple:\n' \
            '/time 3\n' \
            '/time 5\n' \
            '/time 10',

        'DIFFICULTY_CHANGE' : \
            'Nivell de dificultat dels captchas canviat a {}.',

        'DIFFICULTY_NOT_NUM' : \
            'El nivell de dificultat proporcionat no és un nombre.',

        'DIFFICULTY_NOT_ARG' : \
            'El comandament necessita un nivell de dificultat a establir (d\'1 a 5).\n' \
            '\n' \
            'Exemple:\n' \
            '/difficulty 1\n' \
            '/difficulty 2\n' \
            '/difficulty 3\n' \
            '/difficulty 4\n' \
            '/difficulty 5',

        'CAPTCHA_MODE_CHANGE' : \
            'Mode-caràcter dels capcthas canviat a "{}".',

        'CAPTCHA_MODE_INVALID' : \
            'Mode-caràcter invàlid. Les maneres disponibles són: "nums", "hex" i "ascii".\n' \
            '\n' \
            'Exemple:\n' \
            '/captcha_mode nums\n' \
            '/captcha_mode hex\n' \
            '/captcha_mode ascii',

        'CAPTCHA_MODE_NOT_ARG' : \
            'El comandament necessita la manera caràcter a establir. Les maneres disponibles ' \
            'són:\n' \
            '- Captchas numèrics ("nums").\n' \
            '- Captchas hexadecimals, amb números i lletres A-F ("hex").\n' \
            '- Captchas amb números i lletres A-Z (ascii ").\n' \
            '\n' \
            'Exemple:\n' \
            '/captcha_mode nums\n' \
            '/captcha_mode hex\n' \
            '/captcha_mode ascii',

        'NEW_USER_CAPTCHA_CAPTION':
            'Hola{}, benvingut/da a {}, si us plau envia un missatge amb el número que apareix ' \
            'en aquesta imatge per a verificar que ets un humà. Si no resols aquest captcha en ' \
            '{} min, seràs kickejat del grup automàticament.',

        'CAPTHA_SOLVED':
            'Captcha resolt, usuari verificat.\n' \
            'Benvingut/da al grup {}',

        'CAPTCHA_INCORRECT_0':
            'Aquest no és el número correcte. Intenta-ho una altra vegada...',

        'CAPTCHA_INCORRECT_1':
            'Aquest no és el número correcte. Fixa-t\'hi bé, el captcha té 4 xifres...',

        'NEW_USER_KICK':
            '{} no ha completat el captcha a temps. L\'"usuari" ha estat kickejat.',

        'NEW_USER_KICK_NOT_RIGHTS':
            '{} no ha completat el captcha a temps. L\'"usuari" hauria de ser kickejat, però no ' \
            'se m\'han donat els privilegis d\'administració necessaris per a expulsar usuaris ' \
            'del grup.',

        'NEW_USER_KICK_NOT_IN_CHAT':
            '{} no ha completat el captcha a temps. Estava a punt de kickejar l\'"usuari", però ' \
            'ja no és al grup (ha sortit del grup o ha estat kickejat/banejat per un altre Admin).',

        'BOT_CANT_KICK':
            '{} no ha completat el captcha a temps. He intentat kickejar l\'"usuari", però degut ' \
            'a un problema inesperat (potser relacionat amb la xarxa o el servidor), no ho he ' \
            'pogut fer.',

        'CANT_DEL_MSG':
            'He intentat esborrar aquest missatge, però no se m\'han donat els privilegis ' \
            'd\'administració necessaris per tal d\'eliminar els missatges que no són meus.',

        'NEW_USER_BAN':
            'Atenció: Aquesta és la tercera vegada que l\'usuari {} ha intentat unir-se al grup ' \
            'i no ha pogut resoldre el captcha. L\'"usuari" ha estat banejat. Per permetre que ' \
            'intenti entrar novament al grup, un Admin ha de treure la restricció de l\'usuari ' \
            'de forma manual en les opcions d\'administració del grup.',

        'NEW_USER_BAN_NOT_IN_CHAT':
            'Atenció: Aquesta és la tercera vegada que l\'usuari {} ha intentat unir-se al grup ' \
            'i no ha pogut resoldre el captcha. L\'"usuari" hauria de ser banejat, però ja no és ' \
            'al grup (ha sortit del grup o ha estat kickejat/banejat per un Admin).',

        'NEW_USER_BAN_NOT_RIGHTS':
            'Atenció: Aquesta és la tercera vegada que l\'usuari {} ha intentat unir-se al grup ' \
            'i no ha pogut resoldre el captcha. L\'"usuari" hauria de ser banejat, però no se ' \
            'm\'han donat els privilegis d\'administració necessaris per a expulsar usuaris del ' \
            'grup.',

        'BOT_CANT_BAN':
            'Atenció: Aquesta és la tercera vegada que l\'usuari {} ha intentat unir-se al grup ' \
            'i no ha pogut resoldre el captcha. L\'"usuari" hauria de ser banejat, però degut a ' \
            'un problema inesperat (potser relacionat amb la xarxa o el servidor), no ho he ' \
            'pogut fer.',

        'SPAM_DETECTED_RM':
            'S\'ha detectat un missatge que conté una URL (o alias) enviat per {}, que encara no ' \
            'ha resolt el captcha. El missatge ha estat eliminat a fi de tenir un Telegram ' \
            'lliure d\'Spam :)',

        'SPAM_DETECTED_NOT_RM':
            'S\'ha detectat un missatge amb URL (o alias) enviat per {}, que encara no ha resolt ' \
            'el captcha. He intentat esborrar el missatge, però no se m\'han donat els ' \
            'privilegis d\'administració necessaris per tal d\'eliminar missatges que no són meus.',

        'NOT_TEXT_MSG_ALLOWED':
            'Eliminat un missatge que no és de text (imatge, àudio, arxiu...) enviat per {}, a ' \
            'fi de tenir un Telegram lliure d\'Spam.\n' \
            '\n' \
            'Podràs enviar missatges que no siguin de text un cop hagis resolt el captcha.',

        'OTHER_CAPTCHA_BTN_TEXT':
            'Un altre Captcha',

        'ENABLE':
            'Protecció captcha activada. Desactiva-la amb el comandament /disable.',

        'DISABLE':
            'Protecció captcha desactivada. Activa-la amb el comandament /enable.',

        'ALREADY_ENABLE':
            'La protecció captcha ja està activada.',

        'ALREADY_DISABLE':
            'La protecció captcha ja està desactivada.',

        'CAN_NOT_GET_ADMINS':
            'No es pot usar aquest comandament en el xat actual.',

        'VERSION':
            'Vesrsió actual del Bot: {}',

        'ABOUT_MSG':
            'Aquest és un Bot de software lliure open-source amb llicència GNU-GPL, ' \
            'desenvolupat per {}\n' \
            '\n' \
            'Pots consultar el codi aquí:\n' \
            '{}\n' \
            '\n' \
            'T\'agrada el que faig? Convida\'m a un cafè.\n' \
            'Paypal:\n' \
            '{}\n' \
            '\n' \
            'BTC:\n' \
            '{}',

        'COMMANDS' : \
            'Llista de comandaments:\n' \
            '————————————————\n' \
            '/start - Mostra la informació inicial sobre el Bot.\n' \
            '\n' \
            '/help - Mostra la informació d\'ajuda.\n' \
            '\n' \
            '/commands - Mostra el missatge actual. Informació sobre tots els comandaments ' \
            'disponibles i la seva descripció.\n' \
            '\n' \
            '/language - Permet canviar l\'idioma en que parla el Bot. Idiomes actualment ' \
            'disponibles: en (anglès) - es (castellà) - ca (català) - ' \
            'pt_br (portuguès de Brasil).\n' \
            '\n' \
            '/time - Permet canviar el temps disponible per a resoldre un captcha.\n' \
            '\n' \
            '/enable - Activa la protecció captcha en el grup.\n' \
            '\n' \
            '/disable - Desactiva la protecció captcha en el grup.\n' \
            '\n' \
            '/version - Consulta la versió del Bot.\n' \
            '\n' \
            '/about - Mostra la informació "sobre..." del Bot.',
    },
    'PT_BR' : {
        'START' : \
            'Olá, eu sou um Bot que envia um captcha de imagem para cada novo usuário que entra ' \
            'no grupo e expulsa aquele que não enviar o captcha no tempo definido.\n' \
            '\n' \
            'Se um usuário tentar entrar no grupo 3 vezes sem enviar o captcha corretamente, vou ' \
            'assumir que esse "usuário" é um Bot, e ele será banido. Também, qualquer mensagem ' \
            'que contenha um URL que tenha sido enviado por um novo "usuário" antes da conclusão ' \
            'do captcha, será considerada Spam e será excluída.\n' \
            '\n' \
            'Lembre-se de dar privilégios de administrador para que eu possa expulsar-banir ' \
            'usuários e excluir mensagens do grupo.\n' \
            '\n' \
            'Confira o comando /help para saber mais sobre como me usar.\n' \
            '\n' \
            'Eu sou útil? Confira o comando /about e considere fazer uma doação para me manter ' \
            'ativo.',

        'HELP' : \
            'Ajuda do Bot:\n' \
            '————————————————\n' \
            '- Eu sou um Bot que envia um captcha para cada novo usuário que entra no grupo e ' \
            'expulsa aquele que não enviar o captcha no tempo definido.\n' \
            '\n' \
            '- Se um usuário tentar entrar no grupo 3 vezes sem enviar o captcha corretamente, ' \
            'vou assumir que esse “usuário” é um Bot, e ele será banido.\n' \
            '\n' \
            '- Qualquer mensagem que contenha um URL que tenha sido enviado por um novo ' \
            '"usuário" antes da conclusão do captcha, será considerada Spam e será excluída.\n' \
            '\n' \
            '- Você tem que me dar privilégios de administrador para que eu possa expulsar e ' \
            'banir usuários, e remover mensagens.\n' \
            '\n' \
            '- Para manter o grupo limpo, eu removo automaticamente todas as mensagens ' \
            'relacionadas a mim quando um captacha não é enviado e o usuário é expulso (depois ' \
            'de 5 minutos).\n' \
            '\n' \
            '- O tempo de espera para que o usuário envie o captcha é de 5 minutos, mas ele pode ' \
            'ser configurado usando o comando /time.\n' \
            '\n' \
            '- Você pode ativar ou desativar a proteção captcha usando os comandos /enable e ' \
            '/disable.\n' \
            '\n' \
            '- Comandos de configuração somente podem ser usados pelos  Administradores do ' \
            'grupo.\n' \
            '\n' \
            '- Você pode definir o idioma que eu falo usando o comando /language.\n' \
            '\n' \
            '- Você pode configurar o grau de dificuldade do captcha usando a opção ' \
            '/difficulty.\n' \
            '\n' \
            'Você pode definir se o captacha terá apenas números (o padrão) ou números e letras, ' \
            'usando a opção /change_mode.'
            '\n' \
            '- Use a opção /commands para ver a lista de todos os comandos com uma breve ' \
            'descrição de cada um deles.',

        'CMD_NOT_ALLOW' : \
            'Apenas um Admin pode usar esse comando',

        'LANG_CHANGE' : \
            'Idioma definido para Português (Brasil).',

        'LANG_SAME' : \
            'Eu já estou em Português (Brasil).\n' \
            '\n' \
            'Quem sabe você quer usar:\n' \
            '/language en\n' \
            '/language es\n' \
            '/language ca',

        'LANG_BAD_LANG' : \
            'Idioma inválido. Os idiomas disponíveis são Inglês, Espanhol, Catalão e ' \
            'Português (Brasil). Defina um deles usando "en", "es", "ca" ou "pt_br".\n' \
            '\n' \
            'Exemplo:\n' \
            '/language en\n' \
            '/language es\n' \
            '/language ca\n' \
            '/language pt_br',

        'LANG_NOT_ARG' : \
            'O comando exige o idioma que será usado (en – inglês, es – espanhol, ' \
            'ca - catalão, pt_br – português (Brasil)).\n' \
            '\n' \
            'Exemplo:\n' \
            '/language en\n' \
            '/language es\n' \
            '/language ca\n' \
            '/language pt_br',

        'TIME_CHANGE' : \
            'Tempo para enviar o captcha modificado com sucesso para {} minutos.',

        'TIME_MAX_NOT_ALLOW' : \
            'O tempo máximo para resolver o captcha é de 120 minutos. Tempo não mudado.',

        'TIME_NOT_NUM' : \
            'O tempo fornecido não é um número integral.',

        'TIME_NOT_ARG' : \
            'O comando exige um valor para o tempo (em minutos).\n' \
            '\n' \
            'Exemplo:\n' \
            '/time 3\n' \
            '/time 5\n' \
            '/time 10',

        'DIFFICULTY_CHANGE' : \
            'O nível de dificuldade do captcha mudou para {}.',

        'DIFFICULTY_NOT_NUM' : \
            'O nível de dificuldade fornecido não é um número.',

        'DIFFICULTY_NOT_ARG' : \
            'O comando exige um nível de deficuldade como argumento (de 1 a 5).\n' \
            '\n' \
            'Exemplo:\n' \
            '/difficulty 1\n' \
            '/difficulty 2\n' \
            '/difficulty 3\n' \
            '/difficulty 4\n' \
            '/difficulty 5',

        'CAPTCHA_MODE_CHANGE' : \
            'O modo-carater do captcha mudou para "{}".',

        'CAPTCHA_MODE_INVALID' : \
            'Modo-caracter inválido. As opções disponíveis são: "nums", "hex" ou "ascii".\n' \
            '\n' \
            'Exemplo:\n' \
            '/captcha_mode nums\n' \
            '/captcha_mode hex\n' \
            '/captcha_mode ascii',

        'CAPTCHA_MODE_NOT_ARG' : \
            'O comando exite um modo definido. As opções disponíveis são:\n' \
            '- Captchas numéricos ("nums").\n' \
            '- Captchas hexadecimais, com números e letras A-F ("hex").\n' \
            '- Captchas com números e letras A-Z (ascii").\n' \
            '\n' \
            'Exemplo:\n' \
            '/captcha_mode nums\n' \
            '/captcha_mode hex\n' \
            '/captcha_mode ascii',

        'NEW_USER_CAPTCHA_CAPTION' : \
            'Olá {}, seja bem-vindo ao {}. Por favor envie uma mensagem com o número que ' \
            'aparece neste captcha para que possamos nos certificar que você é humano. Se você ' \
            'não enviar o captcha em {} minutos, você será automaticamente expulso do grupo.',

        'CAPTHA_SOLVED' : \
            'Captcha enviado, usuário verificado.\nSeja bem-vindo ao grupo {}',

        'CAPTCHA_INCORRECT_0' : \
            'Esse não é o número correto. Tente de novo...',

        'CAPTCHA_INCORRECT_1' : \
            'Esse não é o número correto. Olhe com atenção pois o captcha tem 4 números...',

        'NEW_USER_KICK' : \
            '{} não enviou o captcha em tempo hábil. O "Usuário" foi expulso.',

        'NEW_USER_KICK_NOT_RIGHTS' : \
            '{} não completou o captcha em tempo. Eu tentei expulsar o "usuário", mas eu não ' \
            'tenho poderes administrativos para expulsar usuários do grupo.',

        'NEW_USER_KICK_NOT_IN_CHAT' : \
            '{} não completou o captcha em tempo. Eu tentei expulsar o "usuário", mas o usuário ' \
            'não está mais no grupo (ele saiu ou foi expulso por um Admin).',

        'BOT_CANT_KICK' : \
            '{} não completou o captcha em tempo. Eu tentei expulsar o "usuário", mas algo deu ' \
            'errado (talvez algo relacionado à rede ou servidor). Não pude fazê-lo.',

        'CANT_DEL_MSG' : \
            'Eu tentei apagar essa mensagem, mas eu não tenho poderes administrativos para ' \
            'remover mensagens que não foram enviadas por mim',

        'NEW_USER_BAN' : \
            'Alerta: Esta é a terceira vez que {} tenta entrar no grupo mas falha ao enviar o ' \
            'captcha. O "usuário" foi banido. Para deixá-lo entrar de novo, um administrador tem ' \
            'que remover as restrições, manualmente..',

        'NEW_USER_BAN_NOT_IN_CHAT' : \
            'Alerta: Esta é a terceira vez que {} tenta entrar no grupo mas falha ao enviar o ' \
            'captcha. Eu tentei banir o "usuário", mas ele não está mais no grupo (ele saiu ou ' \
            'foi expulso por um Admin).',

        'NEW_USER_BAN_NOT_RIGHTS' : \
            'Alerta: Esta é a terceira vez que {} tenta entrar no grupo mas falha ao enviar o ' \
            'captcha. Eu tentei banir o "usuário", mas eu não tenho poderes administrativos para ' \
            'banir usuários do grupo.',

        'BOT_CANT_BAN' : \
            'Alerta: Esta é a terceira vez que {} tenta entrar no grupo mas falha ao enviar o ' \
            'captcha. Eu tentei banir o "usuário", mas algo deu errado (talvez algo relacionado ' \
            'à rede ou servidor). Não pude fazê-lo.',

        'SPAM_DETECTED_RM' : \
            'Detectou uma mensagem com um URL (ou alias) de {}, que ainda não resolveu o ' \
            'captcha. A mensagem foi removida em prol de um Telegram livre de spam :)',

        'SPAM_DETECTED_NOT_RM' : \
            'Detectou uma mensagem com um URL (ou alias) de {}, que ainda não resolveu o ' \
            'captcha. Eu tentei apagar essa mensagem, mas eu não tenho poderes administrativos ' \
            'para remover mensagens que não foram enviadas por mim.',

        'NOT_TEXT_MSG_ALLOWED' : \
            'Removida uma mensagem que não é de texto (imagem, áudio, arquivo...) de {}, por ' \
            'causa de um Telegram livre de spam\n.' \
            '\n' \
            'Você pode enviar mensagens sem texto depois de ter resolvido o captcha.',

        'OTHER_CAPTCHA_BTN_TEXT' : \
            'Outro Captcha',

        'ENABLE' : \
            'Proteção Captcha ativada. Desative com o comando /disable.',

        'DISABLE' : \
            'Proteção Captcha desativada. Ative com o comando /enable.',

        'ALREADY_ENABLE' : \
            'A proteção captcha já está ativada.',

        'ALREADY_DISABLE' : \
            'A proteção captcha já está desativada.',

        'CAN_NOT_GET_ADMINS' : \
            'Não posso usar esse comando neste chat.',

        'VERSION' : \
            'Versão atual do Bot: {}',

        'ABOUT_MSG' : \
            'Este é um Software Livre licenciado pela GNU-GPL Bot desenvolvido pelo {}.\n' \
            '\n' \
            'Você pode acessar o código fonte aqui:\n' \
            '{}\n' \
            '\n' \
            'Gosta do meu trabalho? Me pague um café.\n' \
            '\n' \
            'Paypal:\n' \
            '{}\n' \
            '\n' \
            'BTC:\n' \
            '{}',

        'COMMANDS' : \
            'Lista de comandos:\n' \
            '————————————————\n' \
            '/start - Mostrar informações básicas sobre o bot.\n' \
            '\n' \
            '/help - Mostra informações de ajuda.\n' \
            '\n' \
            '/commands - Mostra a lista de todos os comandos disponíveis e suas descrições.\n' \
            '\n' \
            '/language - Permite definir o idioma das mensagens do bot. Os idiomas disponíveis ' \
            'são: en (inglês) - es (espanhol) - pt_br (português BR).\n' \
            '\n' \
            '/time - Permite alterar o tempo disponível para resolver um captcha.\n' \
            '\n' \
            '/enable - Ativa a proteção captcha no grupo.\n' \
            '\n' \
            '/disable - Desativa a proteção captcha no grupo.\n' \
            '\n' \
            '/version - Mostra a versão do Bot.\n' \
            '\n' \
            '/about - Mostra informações "sobre".'
    }
}
