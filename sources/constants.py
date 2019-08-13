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
    13/08/2019
Version:
    1.4.16
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
    'VERSION' : '1.4.16 (13/08/2019)' # Bot version
}

TEXT = {
    'EN' : {
        'START' : \
            'Hello, I am a Bot that send an image captcha for each new user who joins a group, ' \
            'and kick anyone that can\'t solve the captcha within a specified time.\n' \
            '\n' \
            'If a user tries to join the group 5 times in a row and never solves the captcha, I ' \
            'will assume that this "user" is a bot, and it will be banned. Also, any message ' \
            'that contains a URL sent by a new "user" before the captcha is completed, will be ' \
            'considered spam and will be deleted.\n' \
            '\n' \
            'Remember to give me administration privileges to kick-ban users and remove ' \
            'messages.\n' \
            '\n' \
            'Check /help command for more information about my usage.\n' \
            '\n' \
            'Am I useful? Check /about command and consider making a donation to keep me active.',

        'HELP' : \
            'Bot help:\n' \
            '————————————————\n' \
            '- I am a Bot that send a captcha for each new user who joins a group, and kick any ' \
            'of them that can\'t solve the captcha within a specified time.\n' \
            '\n' \
            '- If a user tries to join the group 5 times in a row and never solves the captcha, ' \
            'I will assume that the "user" is a bot, and it will be banned.\n' \
            '\n' \
            '- Any message that contains an URL that has been sent by a new "user" before ' \
            'captcha is completed, will be considered spam and will be deleted.\n' \
            '\n' \
            '- You need to grant me Administration rights for kick users and remove messages.\n' \
            '\n' \
            '- To preserve a clean group, I auto-remove all messages related to me when a ' \
            'captcha is not solved and the user was kicked (after 5 minutes).\n' \
            '\n' \
            '- The time that new users have to solve the captcha is 5 minutes by default, but it ' \
            'can be configured using the command /time.\n' \
            '\n' \
            '- You can turn captcha protection on/off using the commands /enable and ' \
            '/disable.\n' \
            '\n' \
            '- Configuration commands can only be used by group Administrators.\n' \
            '\n' \
            '- You can change the language that I speak, using the command /language.\n' \
            '\n' \
            '- You can configure captcha difficulty level using command /difficulty.\n' \
            '\n' \
            '- You can set captcha to use just numbers (default) or full numbers and letters, ' \
            'using command /captcha_mode.\n' \
            '\n' \
            '- Check /commands to get a list of all avaliable commands, and a short ' \
            'description of all of them.',

        'CMD_NOT_ALLOW' : \
            'Only an Admin can use this command',

        'LANG_CHANGE' : \
            'Language changed to English.',

        'LANG_SAME' : \
            'I am already in English.\n' \
            '\n' \
            'Did you mean:\n' \
            '/language es\n' \
            '/language ca\n' \
            '/language gl\n' \
            '/language pt_br\n' \
            '/language zh_cn',

        'LANG_BAD_LANG' : \
            'Invalid language provided. The languages currently supported are English, Spanish, ' \
            'Catalan, Galician, Portuguese (Brazil) and Chinese (Mainland terms, CN). Change to ' \
            'any of them using "en", "es", "ca", "gl", pt_br" or "zh_cn".\n' \
            '\n' \
            'Examples:\n' \
            '/language en\n' \
            '/language es\n' \
            '/language ca\n' \
            '/language gl\n' \
            '/language pt_br\n' \
            '/language zh_cn',

        'LANG_NOT_ARG' : \
            'The command needs a language to set (en - English, es - Spanish, ' \
            'ca - Catalan, gl - Galician, pt_br - Portuguese from Brazil, zh_cn - Chinese ' \
            'Mainland).\n' \
            '\n' \
            'Examples:\n' \
            '/language en\n' \
            '/language es\n' \
            '/language ca\n' \
            '/language gl\n' \
            '/language pt_br\n' \
            '/language zh_cn',

        'TIME_CHANGE' : \
            'Time to solve the captcha successfully changed to {} minutes.',

        'TIME_MAX_NOT_ALLOW' : \
            'The maximum allowed captcha solve time is 120 minutes. The time has not been changed.',

        'TIME_NOT_NUM' : \
            'The provided time is not an integer number.',

        'TIME_NOT_ARG' : \
            'The command needs a time value to set (in minutes).\n' \
            '\n' \
            'Examples:\n' \
            '/time 3\n' \
            '/time 5\n' \
            '/time 10',

        'DIFFICULTY_CHANGE' : \
            'Captcha difficulty successfully changed to level {}.',

        'DIFFICULTY_NOT_NUM' : \
            'The provided captcha difficulty is not a number.',

        'DIFFICULTY_NOT_ARG' : \
            'The command needs a difficulty level to set (from 1 to 5).\n' \
            '\n' \
            'Examples:\n' \
            '/difficulty 1\n' \
            '/difficulty 2\n' \
            '/difficulty 3\n' \
            '/difficulty 4\n' \
            '/difficulty 5',

        'CAPTCHA_MODE_CHANGE' : \
            'Captcha character-mode successfully changed to "{}".',

        'CAPTCHA_MODE_INVALID' : \
            'Invalid captcha character-mode. Supported modes are: "nums", "hex" and "ascii".\n' \
            '\n' \
            'Example:\n' \
            '/captcha_mode nums\n' \
            '/captcha_mode hex\n' \
            '/captcha_mode ascii',

        'CAPTCHA_MODE_NOT_ARG' : \
            'The command needs a character-mode to set. Available modes are:\n' \
            '- Numeric Captchas ("nums").\n' \
            '- Hexadecimal Captchas, numbers and characters A-F ("hex").\n' \
            '- Numbers and characters A-Z Captchas ("ascii").\n' \
            '\n' \
            'Examples:\n' \
            '/captcha_mode nums\n' \
            '/captcha_mode hex\n' \
            '/captcha_mode ascii',

        'NEW_USER_CAPTCHA_CAPTION' : \
            'Hello {}, welcome to {}, please send a message with the number that appears in this ' \
            'captcha to verify that you are a human. If you don\'t resolve the captcha in {} ' \
            'mins, you will be automatically kicked from the group.',

        'CAPTHA_SOLVED' : \
            'Captcha solved, user verified.\nWelcome to the group {}',

        'CAPTCHA_INCORRECT_0' : \
            'That is not the correct number. Try again...',

        'CAPTCHA_INCORRECT_1' : \
            'That is not the correct number. Check closely, the captcha has 4 numbers...',

        'NEW_USER_KICK' : \
            '{} has not completed the captcha in time. "User" was kicked.',

        'NEW_USER_KICK_NOT_RIGHTS' : \
            '{} has not completed the captcha in time. I tried to kick the "User", but I ' \
            'don\'t have administration rights to kick users in the group.',

        'NEW_USER_KICK_NOT_IN_CHAT' : \
            '{} has not completed the captcha in time. I tried to kick the "User", but the ' \
            'user is not in the group (has left the group or has been kicked by an Admin).',

        'BOT_CANT_KICK' : \
            '{} has not completed the captcha in time. I tried to kick the "User", but due to ' \
            'an unexpected problem (maybe network/server related), I can\'t do it.',

        'CANT_DEL_MSG' : \
            'I tried to delete this message, but I don\'t have the administration rights to ' \
            'remove messages that have not been sent by me.',

        'NEW_USER_BAN' : \
            'Warning: This is the fifth time that {} has tried to join the group and failed to ' \
            'solve the captcha. "User" was banned. To let him/her enter again, an Admin has to ' \
            'manually remove the restrictions of this "user".',

        'NEW_USER_BAN_NOT_IN_CHAT' : \
            'Warning: This is the fifth time that {} has tried to join the group and failed to ' \
            'solve the captcha. I tride to ban the "User", but the user is not in the group ' \
            '(has left the group or has been kicked/banned by an Admin).',

        'NEW_USER_BAN_NOT_RIGHTS' : \
            'Warning: This is the fifth time that {} has tried to join the group and failed to ' \
            'solve the captcha. I tried to ban the "User", but I don\'t have administration ' \
            'rights to ban users in the group.',

        'BOT_CANT_BAN' : \
            'Warning: This is the fifth time that {} has tried to join the group and failed to ' \
            'solve the captcha. I tried to ban the "User", but due to an unexpected problem ' \
            '(maybe network/server related), I can\'t do it.',

        'SPAM_DETECTED_RM' : \
            'Detected a message with a URL (or alias) from {}, who has not solved the ' \
            'captcha yet. The message has been removed for the sake of keeping Telegram free of ' \
            'Spam :)',

        'SPAM_DETECTED_NOT_RM' : \
            'Message with an URL (or an alias) detected from {}, who has not solved the captcha ' \
            'yet. I tried to remove the Spam message, but I don\'t have administration rights ' \
            'to remove messages that have not been sent by me.',

        'NOT_TEXT_MSG_ALLOWED' : \
            'Removed a non-text message (image, audio, file...) from {}, for the sake of keeping ' \
            'Telegram free of Spam.\n' \
            '\n' \
            'You can send non-text messages after you have solved the captcha.',

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
            'Current Bot version: {}',

        'ABOUT_MSG' : \
            'This Bot is free software and open-sourced under the GNU-GPL license.\n' \
            'Bot Developed by {}.\n' \
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
            '/commands - Shows this message. Information about all the available commands ' \
            'and their description.\n' \
            '\n' \
            '/language - Allows to change the language of the bot\'s messages. Currently ' \
            'available languages: en (English) - es (Spanish) - ca (Catalan) - gl (Galician) - ' \
            'pt_br (Portuguese from Brazil) - zh_cn (Chinese, Mainland terms).\n' \
            '\n' \
            '/time - Allows changing the time available to solve a captcha.\n' \
            '\n' \
            '/difficulty - Allows changing captcha difficulty level (from 1 to 5).\n' \
            '\n' \
            '/captcha_mode - Allows changing captcha character-mode (nums: just numbers, ' \
            'hex: numbers and A-F chars, ascii: numbers and A-Z chars).\n' \
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
            'Hola, soy un Bot que envía una imagen captcha a cada nuevo usuario que se une al ' \
            'grupo, y expulso (kick) a los que no resuelvan el captcha en un tiempo ' \
            'determinado.\n' \
            '\n' \
            'Si un usuario ha intentado unirse al grupo 5 veces y nunca consiguió resolver el ' \
            'captcha, supondré que ese "usuario" es un Bot y, trás expulsarlo, lo bloquearé ' \
            '(ban) para que no pueda volver a entrar en el grupo. Además, cualquier mensaje que ' \
            'contenga una URL y haya sido enviado por un nuevo "usuario" antes de que este ' \
            'haya resuelto el captcha, será considerado un mensaje de Spam y será borrado.\n' \
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
            'expulso (kick) a los que no resuelvan el captcha en un tiempo determinado.\n' \
            '\n' \
            '- Si un usuario ha intentado unirse al grupo 5 veces y nunca consiguió resolver ' \
            'el captcha, supondré que ese "usuario" es un Bot y, trás expulsarlo, lo ' \
            'bloquearé (ban) para que no pueda volver a entrar en el grupo.\n' \
            '\n' \
            '- Cualquier mensaje que contenga una URL y haya sido enviado por un nuevo "usuario" ' \
            'antes de que este haya resuelto el captcha, será considerado un mensaje de Spam y ' \
            'será borrado.\n' \
            '\n' \
            '- Debes darme permisos de Administración para suspender usuarios y eliminar ' \
            'mensajes.\n' \
            '\n' \
            '- Para mantener limpio el grupo, elimino aquellos mensajes que tengan relación ' \
            'conmigo cuando no se haya resuelto el captcha y el usuario haya sido expulsado ' \
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
            'números y letras, a través del comando /captcha_mode.\n' \
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
            '/language gl\n' \
            '/language pt_br\n' \
            '/language zh_cn',

        'LANG_BAD_LANG' : \
            'Idioma inválidado. Los idiomas actualmente soportados son inglés, español, ' \
            'catalán, gallego, portugués de Brasil y chino. Cambia a uno de ellos mediante las ' \
            'etiquetas "en", "es", "ca", "gl", pt_br" o "zh_cn".\n' \
            '\n' \
            'Ejemplos:\n' \
            '/language en\n' \
            '/language es\n' \
            '/language ca\n' \
            '/language gl\n' \
            '/language pt_br\n' \
            '/language zh_cn',

        'LANG_NOT_ARG' : \
            'El comando necesita un idioma que establecer (en - inglés, es - español, ' \
            'ca - catalán, gl - gallego, pt_br - portugués de Brasil, zh_cn - chino).\n' \
            '\n' \
            'Ejemplos:\n' \
            '/language en\n' \
            '/language es\n' \
            '/language ca\n' \
            '/language gl\n' \
            '/language pt_br\n' \
            '/language zh_cn',

        'TIME_CHANGE' : \
            'Tiempo para resolver el captcha cambiado a {} minutos.',

        'TIME_MAX_NOT_ALLOW' : \
            'El tiempo máximo para resolver el captcha son 120 minutos. No se cambió el tiempo.',

        'TIME_NOT_NUM' : \
            'El tiempo entregado no es un número entero.',

        'TIME_NOT_ARG' : \
            'El comando necesita un valor de tiempo a establecer (en minutos).\n' \
            '\n' \
            'Ejemplos:\n' \
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
            'Ejemplos:\n' \
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
            'Ejemplos:\n' \
            '/captcha_mode nums\n' \
            '/captcha_mode hex\n' \
            '/captcha_mode ascii',

        'CAPTCHA_MODE_NOT_ARG' : \
            'El comando necesita el modo-caracter a establecer. Los modos disponibles son:\n' \
            '- Captchas numéricos ("nums").\n' \
            '- Captchas hexadecimales, con números y letras A-F ("hex").\n' \
            '- Captchas con números y letras A-Z ("ascii").\n' \
            '\n' \
            'Ejemplos:\n' \
            '/captcha_mode nums\n' \
            '/captcha_mode hex\n' \
            '/captcha_mode ascii',

        'NEW_USER_CAPTCHA_CAPTION' : \
            'Hola {}, bienvenido a {}, por favor envía un mensaje con el número que aparece ' \
            'en esta imagen para verificar que eres un humano. Si no resuelves este captcha en ' \
            '{} mins, serás expulsado (kick) del grupo automáticamente.',

        'CAPTHA_SOLVED' : \
            'Captcha resuelto, usuario verificado.\nBienvenido al grupo {}',

        'CAPTCHA_INCORRECT_0' : \
            'Ese no es el número correcto. Inténtalo nuevamente...',

        'CAPTCHA_INCORRECT_1' : \
            'Ese no es el número correcto. Fijate bien, el captcha tiene 4 numeros...',

        'NEW_USER_KICK' : \
            '{} no completó el captcha a tiempo. El "usuario" fue expulsado (kick).',

       'NEW_USER_KICK_NOT_RIGHTS' : \
            '{} no completó el captcha a tiempo. El "usuario" debería ser expulsado (kick), pero ' \
            'no se me han dado los privilegios de administración necesarios para expulsar ' \
            'usuarios del grupo.',

        'NEW_USER_KICK_NOT_IN_CHAT' : \
            '{} no completó el captcha a tiempo. Iba a expulsar (kick) al "usuario", pero ya no ' \
            'se encuentra en el grupo (salió del grupo o fue expulsado por un Admin).',

        'BOT_CANT_KICK' : \
            '{} no completó el captcha a tiempo. He intentado expulsar (kick) al "usuario", pero ' \
            'debido a un problema inesperado (quizás relacionado con la red o el servidor), no ' \
            'he podido hacerlo.',

        'CANT_DEL_MSG' : \
            'He intentado borrar este mensaje pero no se me han dado los privilegios de ' \
            'administración necesarios para eliminar mensajes que no son míos.',

        'NEW_USER_BAN' : \
            'Atención: Esta es la quinta vez que el usuario {} ha intentado unirse al grupo ' \
            'y no pudo resolver el captcha. El "usuario" fue expulsado y bloqueado (ban). ' \
            'Para permitir que intente entrar nuevamente al grupo, un Admin debe de quitar la ' \
            'restricción del usuario de forma manual en las opciones de administración del grupo.',

        'NEW_USER_BAN_NOT_IN_CHAT' : \
            'Atención: Esta es la quinta vez que el usuario {} ha intentado unirse al grupo ' \
            'y no pudo resolver el captcha. El "usuario" debería ser expulsado y bloqueado ' \
            '(ban), pero ya no se encuentra en el grupo (salió del grupo o fue expulsado por ' \
            'un Admin).',

        'NEW_USER_BAN_NOT_RIGHTS' : \
            'Atención: Esta es la quinta vez que el usuario {} ha intentado unirse al grupo ' \
            'y no pudo resolver el captcha. El "usuario" debería ser expulsado y bloqueado ' \
            '(ban), pero no se me han dado los privilegios de administración necesarios para ' \
            'expulsar usuarios del grupo.',

        'BOT_CANT_BAN' : \
            'Atención: Esta es la quinta vez que el usuario {} ha intentado unirse al grupo ' \
            'y no pudo resolver el captcha. El "usuario" debería ser expulsado y bloqueado ' \
            '(ban), pero debido a un problema inesperado (quizás relacionado con la red o el ' \
            'servidor), no he podido hacerlo.',

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
            'disponibles: en (inglés) - es (español) - ca (catalán) - gl (gallego) - ' \
            'pt_br (portugués de Brasil) - zh_cn (Chino, Mainland terms).\n' \
            '\n' \
            '/time - Permite cambiar el tiempo disponible para resolver un captcha.\n' \
            '\n' \
            '/difficulty - Permite cambiar el nivel de dificultad del captcha (de 1 a 5).\n' \
            '\n' \
            '/captcha_mode - Permite cambiar el modo-caracter de los captchas (nums: solo ' \
            'números, hex: números y letras A-F, ascii: números y letras A-Z).\n' \
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
            'Hola, sóc un bot que envia una imatge captcha a cada usuari nou que s\'uneix al ' \
            'grup, i expulso (kick) als que no resolen el captcha en un temps determinat.\n' \
            '\n' \
            'Si un usuari ha intentat unir-se al grup 5 vegades i mai no ha resolt el captcha, ' \
            'suposaré que aquell "usuari" és un bot i el bandejaré (ban). A més, qualsevol ' \
            'missatge que contingui un URL i hagi estat enviat per un "usuari" nou abans que ' \
            'aquest hagi resolt el captcha, serà considerat un missatge brossa (SPAM) \n' \
            'i l\'esborraré.\n' \
            '\n' \
            'Recordeu que per a funcionar de forma adequada heu de donar-me permisos ' \
            'd\'administració per a suspendre (expulsar) usuaris i eliminar missatges del grup.\n' \
            '\n' \
            'Doneu un cop d\'ull a l\'ordre /help per a obtenir més informació sobre el meu ús.\n' \
            '\n' \
            'Us sóc útil? Feu una ullada a l\'ordre /about i penseu en fer una donació ' \
            'per mantenir-me actiu.', 

        'HELP':
            'Ajuda sobre el bot:\n' \
            '————————————————\n' \
            '- Sóc un bot que envia un captcha a cada usuari nou que s\'uneix al grup, i expulso ' \
            '(kick) als que no resolen el captcha en un temps determinat.\n' \
            '\n' \
            '- Si un usuari ha intentat unir-se al grup 5 vegades i mai no ha resolt el captcha, ' \
            'suposaré que aquell "usuari" és un bot i el bandejaré (ban).\n' \
            '\n' \
            '- Qualsevol missatge que contingui un URL i hagi estat enviat per un "usuari" nou ' \
            'abans que aquest hagi resolt el captcha, serà considerat un missatge brossa (SPAM) i ' \
            'l\'esborraré.\n' \
            '\n' \
            '- Heu de donar-me permisos d\'administració per a expulsar usuaris i eliminar ' \
            'missatges.\n' \
            '\n' \
            '- Per tal de mantenir net el grup, elimino aquells missatges que tinguin relació ' \
            'amb mi quan no s\'hagi resolt el captcha i l\'usuari hagi estat expulsat (kick) ' \
            '(transcorreguts 5 minuts).\n' \
            '\n' \
            '- El temps del que disposen els usuaris per a resoldre el captcha són 5 minuts, ' \
            'però es pot canviar mitjançant l\'ordre /time.\n' \
            '\n' \
            '- Podeu activar o desactivar la protecció captcha mitjançant les ordres ' \
            '/enable i /disable.\n' \
            '\n' \
            '- Les ordres de configuració només les poden utilitzar els administradors ' \
            'del grup.\n' \
            '\n' \
            '- Podeu canviar l\'idioma en el que parlo mitjançant l\'ordre /language.\n' \
            '\n' \
            '- Podeu configurar el nivell de dificultat del captcha mitjançant l\'ordre ' \
            '/difficulty.\n' \
            '\n' \
            '- Podeu establir que els captcha només continguin números (per defecte), ' \
            'o números i lletres, a través de l\'ordre /captcha_mode.\n' \
            '\n' \
            '- Doneu un cop d\'ull a l\'ordre /commands per a veure un llistat amb totes les ' \
            'ordres disponibles i una breu descripció de cadascuna.',

        'CMD_NOT_ALLOW':
            'Aquesta ordre només la pot utilitar un administrador.',

        'LANG_CHANGE':
            'S\'ha canviat l\'idioma a català.',

        'LANG_SAME':
            'Ja parlo en català.\n' \
            '\n' \
            'Potser volies dir:\n' \
            '/language en\n' \
            '/language es\n' \
            '/language gl\n' \
            '/language pt_br\n' \
            '/language zh_cn',

        'LANG_BAD_LANG':
            'Idioma no vàlid. Els idiomes que parlo actualment són anglès, castellà, ' \
            'català, galician, portuguès de Brasil i xinès. Canvia a un d\'ells mitjançant les ' \
            'etiquetes "en", "es", "ca", "gl", pt_br" o "zh_cn".\n' \
            '\n' \
            'Exemples:\n' \
            '/language en\n' \
            '/language es\n' \
            '/language ca\n' \
            '/language gl\n' \
            '/language pt_br\n' \
            '/language zh_cn',

        'LANG_NOT_ARG':
            'Cal que especifiqueu un idioma (en - anglès, es - castellà, ' \
            'ca - català, gl - galician, pt_br - portuguès de Brasil, zh_cn - xinès).\n' \
            '\n' \
            'Exemples:\n' \
            '/language en\n' \
            '/language es\n' \
            '/language ca\n' \
            '/language gl\n' \
            '/language pt_br\n' \
            '/language zh_cn',

        'TIME_CHANGE':
            'S\'ha canviat el temps per a resoldre el captcha a {} minuts.',

        'TIME_MAX_NOT_ALLOW':
            'El temps màxim per a resoldre el captcha són 120 minuts. No s\'ha canviat el temps.',

        'TIME_NOT_NUM':
            'El temps introduït no és un número enter.',

        'TIME_NOT_ARG':
            'Cal que especifiqueu un valor de temps (en minuts).\n' \
            '\n' \
            'Exemples:\n' \
            '/time 3\n' \
            '/time 5\n' \
            '/time 10',

        'DIFFICULTY_CHANGE' : \
            'S\'ha canviat el nivell de dificultat dels captcha a {}.',

        'DIFFICULTY_NOT_NUM' : \
            'El nivell de dificultat introduït no és un número.',

        'DIFFICULTY_NOT_ARG' : \
            'Cal que especifiqueu un nivell de dificultat (de l\'1 al 5).\n' \
            '\n' \
            'Exemples:\n' \
            '/difficulty 1\n' \
            '/difficulty 2\n' \
            '/difficulty 3\n' \
            '/difficulty 4\n' \
            '/difficulty 5',

        'CAPTCHA_MODE_CHANGE' : \
            'S\'ha canviat el mode-caràcter dels capctha a "{}".',

        'CAPTCHA_MODE_INVALID' : \
            'Mode-caràcter no vàlid. Els modes disponibles són: "nums", "hex" i "ascii".\n' \
            '\n' \
            'Exemples:\n' \
            '/captcha_mode nums\n' \
            '/captcha_mode hex\n' \
            '/captcha_mode ascii',

        'CAPTCHA_MODE_NOT_ARG' : \
            'Cal que especifiqueu un mode-caràcter. Els modes disponibles ' \
            'són:\n' \
            '- Captcha numèrics ("nums").\n' \
            '- Captcha hexadecimals, amb números i lletres A-F ("hex").\n' \
            '- Captcha amb números i lletres A-Z ("ascii").\n' \
            '\n' \
            'Exemples:\n' \
            '/captcha_mode nums\n' \
            '/captcha_mode hex\n' \
            '/captcha_mode ascii',

        'NEW_USER_CAPTCHA_CAPTION':
            'Hola {}, benvingut/da a {}. Podeu enviar un missatge amb el número que apareix ' \
            'en aquesta imatge per a verificar que sou un humà. Si no resoleu aquest captcha en ' \
            '{} minuts, sereu expulsat del grup automàticament.',

        'CAPTHA_SOLVED':
            'Heu resolt el captcha correctament. Ja sou un usuari verificat.\n' \
            'Benvingut/da al grup, {}',

        'CAPTCHA_INCORRECT_0':
            'Aquest codi no és correcte. Intenteu-ho una altra vegada...',

        'CAPTCHA_INCORRECT_1':
            'Aquest codi no és correcte. Fixeu-vos-hi bé, el captcha té 4 caràcters...',

        'NEW_USER_KICK':
            '{} no ha completat el captcha a temps. L\'"usuari" ha estat expulsat.',

        'NEW_USER_KICK_NOT_RIGHTS':
            '{} no ha completat el captcha a temps. L\'"usuari" hauria de ser expulsat, però no ' \
            'se m\'han donat els permisos d\'administració necessaris per a expulsar usuaris ' \
            'del grup.',

        'NEW_USER_KICK_NOT_IN_CHAT':
            '{} no ha completat el captcha a temps. Estava a punt d\'expulsar l\'"usuari", però ' \
            'ja no és al grup (ha sortit del grup o ha estat expulsat/bandejat per un administrador).',

        'BOT_CANT_KICK':
            '{} no ha completat el captcha a temps. He intentat expulsar l\'"usuari", però a causa ' \
            'd\'un problema inesperat (potser relacionat amb la xarxa o el servidor), no ho he ' \
            'pogut fer.',

        'CANT_DEL_MSG':
            'He intentat esborrar aquest missatge, però no se m\'han donat els permisos ' \
            'd\'administració necessaris per tal d\'eliminar els missatges que no són meus.',

        'NEW_USER_BAN':
            'Atenció! Aquesta és la cinquena vegada que l\'usuari {} ha intentat unir-se al grup ' \
            'i no ha pogut resoldre el captcha. L\'"usuari" ha estat bandejat. Per permetre que ' \
            'intenti entrar novament al grup, un administrador ha de treure la restricció de l\'usuari ' \
            'de forma manual a les opcions d\'administració del grup.',

        'NEW_USER_BAN_NOT_IN_CHAT':
            'Atenció! Aquesta és la cinquena vegada que l\'usuari {} ha intentat unir-se al grup ' \
            'i no ha pogut resoldre el captcha. L\'"usuari" hauria de ser bandejat, però ja no és ' \
            'al grup (ha sortit del grup o ha estat expulsat/bandejat per un administrador).',

        'NEW_USER_BAN_NOT_RIGHTS':
            'Atenció! Aquesta és la cinquena vegada que l\'usuari {} ha intentat unir-se al grup ' \
            'i no ha pogut resoldre el captcha. L\'"usuari" hauria de ser bandejat, però no se ' \
            'm\'han donat els permisos d\'administració necessaris per a expulsar usuaris del ' \
            'grup.',

        'BOT_CANT_BAN':
            'Atenció! Aquesta és la cinquena vegada que l\'usuari {} ha intentat unir-se al grup ' \
            'i no ha pogut resoldre el captcha. L\'"usuari" hauria de ser bandejat, però a causa ' \
            'd\'un problema inesperat (potser relacionat amb la xarxa o el servidor), no ho he ' \
            'pogut fer.',

        'SPAM_DETECTED_RM':
            'S\'ha detectat un missatge que conté un URL (o àlies) enviat per {}, que encara no ' \
            'ha resolt el captcha. He eliminat el missatge per tal de tenir el grup net de brossa :)',

        'SPAM_DETECTED_NOT_RM':
            'S\'ha detectat un missatge amb URL (o àlies) enviat per {}, que encara no ha resolt ' \
            'el captcha. He intentat esborrar el missatge, però no se m\'han donat els ' \
            'permisos d\'administració necessaris per tal d\'eliminar missatges que no són meus.',

        'NOT_TEXT_MSG_ALLOWED':
            'He eliminat un missatge que no és de text (imatge, àudio, fitxer...) enviat per {}, ' \
            'per tal de mantenir el grup net de brossa.\n' \
            '\n' \
            'Podreu enviar missatges que no siguin de text un cop hàgiu resolt el captcha.',

        'OTHER_CAPTCHA_BTN_TEXT':
            'Mostra un altre captcha',

        'ENABLE':
            'S\'ha activat la protecció per captcha. Podeu desactivar-la amb l\'ordre /disable.',

        'DISABLE':
            'S\'ha desactivat la protecció per captcha. Podeu activar-la amb l\'ordre /enable.',

        'ALREADY_ENABLE':
            'La protecció per captcha ja està activada.',

        'ALREADY_DISABLE':
            'La protecció per captcha ja està desactivada.',

        'CAN_NOT_GET_ADMINS':
            'No es pot utilitzar aquesta ordre en el xat actual.',

        'VERSION':
            'La versió actual del bot és: {}',

        'ABOUT_MSG':
            'Aquest és un bot de programari lliure i codi obert (open-source) amb llicència GNU-GPL, ' \
            'desenvolupat per {}\n' \
            '\n' \
            'Podeu consultar el codi font aquí:\n' \
            '{}\n' \
            '\n' \
            'Us agrada el que faig? Convideu-me a un cafè.\n' \
            'Paypal:\n' \
            '{}\n' \
            '\n' \
            'BTC:\n' \
            '{}',

        'COMMANDS' : \
            'Llistat d\'ordres:\n' \
            '————————————————\n' \
            '/start - Mostra la informació inicial sobre el bot.\n' \
            '\n' \
            '/help - Mostra la informació d\'ajuda.\n' \
            '\n' \
            '/commands - Mostra el missatge actual: informació sobre totes les ordres ' \
            'disponibles i la seva descripció.\n' \
            '\n' \
            '/language - Permet canviar l\'idioma en que parla el bot. Idiomes disponibles ' \
            'actualment: en (anglès) - es (castellà) - ca (català) - gl (galician) - ' \
            'pt_br (portuguès de Brasil) - zh_cn (xinès).\n' \
            '\n' \
            '/time - Permet canviar el temps disponible per a resoldre un captcha.\n' \
            '\n' \
            '/difficulty - Permet canviar el nivell de dificultat del captcha (d\'1 a 5).\n' \
            '\n' \
            '/captcha_mode - Permet canviar el mode-caràcter del captcha (nums: només ' \
            'números, hex: números i lletres A-F, ascii: números i lletres A-Z).\n' \
            '\n' \
            '/enable - Activa la protecció per captcha en el grup.\n' \
            '\n' \
            '/disable - Desactiva la protecció per captcha en el grup.\n' \
            '\n' \
            '/version - Consulta la versió del bot.\n' \
            '\n' \
            '/about - Mostra la informació "Quant a..." del bot.',
    },
    'GL' : {
        'START' : \
            'Ola, son un Bot que envía unha imaxe captcha a cada novo usuario que se una ao ' \
            'grupo, e expulso (kick) aos que non resolvan o captcha nun tempo ' \
            'determinado.\n' \
            '\n' \
            'Se un usuario intentouse unir ao grupo 5 veces e nunca conseguiu resolver o ' \
            'captcha, suporei que ese "usuario" é un Bot e, tras expulsalo, bloqueareino ' \
            '(ban) para que non poida volver a entrar no grupo. Además, calquera mensaxe que ' \
            'conteña unha URL e fora enviada por un novo "usuario" antes de que este ' \
            'resolvera o captcha, será considerada unha mensaxe de Spam e será borrada.\n' \
            '\n' \
            'Lembra que para funcionar de maneira adecuada debes darme permisos de ' \
            'administración para suspender usuarios e eliminar mensaxes do grupo.\n' \
            '\n' \
            'Bota un vistazo ao comando /help para coñecer máis información sobre o meu uso.\n' \
            '\n' \
            'Son útil? Bota un vistazo ao comando /about e considera facer unha donación para ' \
            'manterme activo.',

        'HELP' : \
            'Axuda sobre o Bot:\n' \
            '————————————————\n' \
            '- Son un Bot que envía un captcha a cada novo usuario que se une ao grupo, e ' \
            'expulso (kick) aos que no resolvan o captcha nun tempo determinado.\n' \
            '\n' \
            '- Se un usuario intentou unirse ao grupo 5 veces e nunca conseguiu resolver ' \
            'o captcha, suporei que ese "usuario" é un Bot e, tras expulsalo, ' \
            'bloqueareino(ban) para que non poida volver a entrar no grupo.\n' \
            '\n' \
            '- Calquera mensaxe que conteña unha URL e fora enviada por un novo "usuario" ' \
            'antes de que este resolvera o captcha, será considerada unha mensaxe de Spam e ' \
            'será borrada.\n' \
            '\n' \
            '- Debes darme permisos de Administración para suspender usuarios e eliminar ' \
            'mensaxes.\n' \
            '\n' \
            '- Para manter limpio o grupo, elimino aquelas mensaxes que teñan relación ' \
            'conmigo cando no se resolvera o captcha e o usuario sexa expulsado ' \
            '(transcurridos 5 minutos).\n' \
            '\n' \
            '- O tempo que dispoñen os usuarios para resolver o captcha son 5 minutos, pero ' \
            'este tempo pode ser cambiado mediante o comando /time.\n' \
            '\n' \
            '- Podes activar ou desactivar a protección captcha mediante os comandos /enable e ' \
            '/disable.\n' \
            '\n' \
            '- Os comandos de configuracións só poden ser usados polos Administradores ' \
            'do grupo.\n' \
            '\n' \
            '- Podes cambiar o idioma no que falo mediante o comando /language.\n' \
            '\n' \
            '- Podes configurar o nivel de dificultade do captcha mediante o comando ' \
            '/difficulty.\n' \
            '\n' \
            '- Podes establecer que os captchas só conteñan números (por defecto), ou ' \
            'números e letras, a través do comando /captcha_mode.\n' \
            '\n' \
            '- Bota un vistazo ao comando /commands para ver unha lista con todos os comandos ' \
            'dispoñibles e unha breve descripción de cada un deles.',

        'CMD_NOT_ALLOW' : \
            'Só un Admin pode utilizar este comando.',

        'LANG_CHANGE' : \
            'Idioma cambiado a galego.',

        'LANG_SAME' : \
            'Xa estou en galego.\n' \
            '\n' \
            'Quizás querías dicir:\n' \
            '/language en\n' \
            '/language es\n' \
            '/language ca\n' \
            '/language pt_br\n' \
            '/language zh_cn',

        'LANG_BAD_LANG' : \
            'Idioma inválidado. Os idiomas actualmente soportados son inglés, español, ' \
            'catalán, galego, portugués de Brasil e chino. Cambia a un deles mediante ' \
            'as etiquetas "en", "es", "ca", "gl", "pt_br" o "zh_cn".\n' \
            '\n' \
            'Exemplos:\n' \
            '/language en\n' \
            '/language es\n' \
            '/language ca\n' \
            '/language gl\n' \
            '/language pt_br\n' \
            '/language zh_cn',

        'LANG_NOT_ARG' : \
            'O comando necesita un idioma que establecer (en - inglés, es - español, ' \
            'ca - catalán, gl - galego, pt_br - portugués de Brasil, zh_cn - chino).\n' \
            '\n' \
            'Exemplos:\n' \
            '/language en\n' \
            '/language es\n' \
            '/language ca\n' \
            '/language gl\n' \
            '/language pt_br\n' \
            '/language zh_cn',

        'TIME_CHANGE' : \
            'Tempo para resolver o captcha cambiado a {} minutos.',

        'TIME_MAX_NOT_ALLOW' : \
            'O tempo máximo para resolver o captcha son 120 minutos. Non se cambiou o tempo.',

        'TIME_NOT_NUM' : \
            'O tempo entregado non é un número enteiro.',

        'TIME_NOT_ARG' : \
            'O comando necesita un valor de tempo a establecer (en minutos).\n' \
            '\n' \
            'Exemplos:\n' \
            '/time 3\n' \
            '/time 5\n' \
            '/time 10',

        'DIFFICULTY_CHANGE' : \
            'Nivel de dificultade de los captchas cambiado a {}.',

        'DIFFICULTY_NOT_NUM' : \
            'O nivel de dificultade proporcionado non é un número.',

        'DIFFICULTY_NOT_ARG' : \
            'O comando necesita un nivel de dificultade a establecer (do 1 ao 5).\n' \
            '\n' \
            'Exemplos:\n' \
            '/difficulty 1\n' \
            '/difficulty 2\n' \
            '/difficulty 3\n' \
            '/difficulty 4\n' \
            '/difficulty 5',

        'CAPTCHA_MODE_CHANGE' : \
            'Modo-caracter dos capcthas cambiado a "{}".',

        'CAPTCHA_MODE_INVALID' : \
            'Modo-caracter invalido. Os modos dispoñibles son: "nums", "hex" e "ascii".\n' \
            '\n' \
            'Exemplos:\n' \
            '/captcha_mode nums\n' \
            '/captcha_mode hex\n' \
            '/captcha_mode ascii',

        'CAPTCHA_MODE_NOT_ARG' : \
            'O comando necesita o modo-caracter a establecer. Os modos dispoñibles son:\n' \
            '- Captchas numéricos ("nums").\n' \
            '- Captchas hexadecimais, con números e letras A-F ("hex").\n' \
            '- Captchas con números e letras A-Z ("ascii").\n' \
            '\n' \
            'Exemplos:\n' \
            '/captcha_mode nums\n' \
            '/captcha_mode hex\n' \
            '/captcha_mode ascii',

        'NEW_USER_CAPTCHA_CAPTION' : \
            'Ola {}, benvido a {}, por favor envía unha mensaxe co número que aparece ' \
            'nesta imaxe para verificar que eres un humano. Se non resolves ese captcha en ' \
            '{} mins, serás expulsado (kick) do grupo automáticamente.',

        'CAPTHA_SOLVED' : \
            'Captcha resolto, usuario verificado.\nBenvido ao grupo {}',

        'CAPTCHA_INCORRECT_0' : \
            'Ese non é o número correcto. Inténtao novamente...',

        'CAPTCHA_INCORRECT_1' : \
            'Ese non é o número correcto. Fíxate ben, o captcha ten 4 números...',

        'NEW_USER_KICK' : \
            '{} non completou o captcha a tempo. O "usuario" foi expulsado (kick).',

        'NEW_USER_KICK_NOT_RIGHTS' : \
            '{} non completou o captcha a tempo. O "usuario" debería ser expulsado (kick), pero ' \
            'non se me deron os privilexios de administración necesarios para expulsar ' \
            'usuarios do grupo.',

        'NEW_USER_KICK_NOT_IN_CHAT' : \
            '{} non completou o captcha a tempo. Iba expulsar (kick) ao "usuario", pero xa non ' \
            'se encontra no grupo (Saliu do grupo o foi expulsado por un Admin).',

        'BOT_CANT_KICK' : \
            '{} non completou o captcha a tempo. Intentei expulsar (kcik) ao "usuario", pero ' \
            'debido a un problema inesperado (quizais relacionado ca rede ou o servidor), non ' \
            'puiden facelo.',

        'CANT_DEL_MSG' : \
            'Intentei borrar esta mensaxe pero non se me deron os privilexios de ' \
            'administración necesarios para eliminar mensaxes que non son meus.',

        'NEW_USER_BAN' : \
            'Atención: Esta é a quinta vez que o usuario {} intentou unirse ao grupo ' \
            'e non puido resolver o captcha. O "usuario" foi expulsado e bloqueado (ban). ' \
            'Para permitir que intente entrar novamente ao grupo, un Admin debe de quitar a ' \
            'restricción do usuario de forma manual nas opciones de administración do grupo.',

        'NEW_USER_BAN_NOT_IN_CHAT' : \
            'Atención: Esta é a quinta vez que o usuario {} intentou unirse ao grupo ' \
            'e non puido resolver o captcha. O "usuario" debería ser expulsado e bloqueado ' \
            '(ban), pero xa non se encontra no grupo (saíu do grupo ou foi expulsado por ' \
            'un Admin).',

        'NEW_USER_BAN_NOT_RIGHTS' : \
            'Atención: Esta é a quinta vez que o usuario {} intentou unirse ao grupo ' \
            'e non puido resolver o captcha. O "usuario" debería ser expulsado e bloqueado ' \
            '(ban), pero non se me deron os privilexios de administración necesarios para ' \
            'expulsar usuarios do grupo.',

        'BOT_CANT_BAN' : \
            'Atención: Esta é a quinta vez que o usuario {} intentou unirse ao grupo ' \
            'e non puido resolver o captcha. O "usuario" debería ser expulsado e bloqueado ' \
            '(ban), pero debido a un problema inesperado (quizais relacionado ca rede ou o ' \
            'servidor), non puiden facelo.',

        'SPAM_DETECTED_RM' : \
            'Detectouse unha mensaxe que contén unha URL (ou alias) enviado por {}, quen aínda ' \
            'non resolveu o captcha. A mensaxe foi eliminada en aras dun Telegram ' \
            'libre de Spam :)',

        'SPAM_DETECTED_NOT_RM' : \
            'Detectouse unha mensaxe que contén unha URL (ou alias) enviado por {}, quen aínda ' \
            'non resolveu o captcha. Intentei borrar a mensaxe, pero non se me deron os ' \
            'privilexios de administración necesarios para eliminar mensaxes que non son meus.',

        'NOT_TEXT_MSG_ALLOWED' : \
            'Eliminada unha mensaje que non é de texto (imaxe, audio, arquivo...) enviado por ' \
            '{}, en aras dun Telegram libre de Spam.\n' \
            '\n' \
            'Poderás enviar mensaxes que non sexan de texto unha vez que haxas resolto o captcha.',

        'OTHER_CAPTCHA_BTN_TEXT' : \
            'Otro Captcha',

        'ENABLE' : \
            'Protección captcha activada. Desactívaa co comando /disable.',

        'DISABLE' : \
            'Protección captcha desactivada. Actívaa co comando /enable.',

        'ALREADY_ENABLE' : \
            'A protección captcha xa está activada.',

        'ALREADY_DISABLE' : \
            'A protección captcha xa está desactivada.',

        'CAN_NOT_GET_ADMINS' : \
            'Non se pode usar este comando no chat actual.',

        'VERSION' : \
            'Versión actual do Bot: {}',

        'ABOUT_MSG' : \
            'Iste é un Bot de software libre open-source con licencia GNU-GPL, desenrolado por ' \
            '{}.\n' \
            '\n' \
            'Podes consultar o código aquí:\n' \
            '{}\n' \
            '\n' \
            'Gústache o que fago? Invítame a un café.\n' \
            '\n' \
            'Paypal:\n' \
            '{}\n' \
            '\n' \
            'BTC:\n' \
            '{}',

        'COMMANDS' : \
            'Lista de comandos:\n' \
            '————————————————\n' \
            '/start - Mostra a información inicial sobre o Bot.\n' \
            '\n' \
            '/help - Mostra a información de axuda.\n' \
            '\n' \
            '/commands - Mostra a mensaxe actual. Información sobre todos os comandos ' \
            'dispoñibles e a súa descripción.\n' \
            '\n' \
            '/language - Permite cambiar o idioma no que fala o Bot. Idiomas actualmente ' \
            'dispoñibles: en (inglés) - es (español) - ca (catalán) - gl (galego) - ' \
            'pt_br (portugués de Brasil) - zh_cn (Chino, Mainland terms).\n' \
            '\n' \
            '/time - Permite cambiar o tempo dispoñible para resolver un captcha.\n' \
            '\n' \
            '/difficulty - Permite cambiar o nivel de dificultade do captcha (do 1 ao 5).\n' \
            '\n' \
            '/captcha_mode - Permite cambiar o modo-caracter dos captchas (nums: só ' \
            'números, hex: números e letras A-F, ascii: números e letras A-Z).\n' \
            '\n' \
            '/enable - Activa a protección captcha no grupo.\n' \
            '\n' \
            '/disable - Desactiva a protección captcha no grupo.\n' \
            '\n' \
            '/version - Consulta a versión do Bot.\n' \
            '\n' \
            '/about - Mostra a información \"acerca do...\" do Bot.'
    },
    'PT_BR' : {
        'START' : \
            'Olá, eu sou um Bot que envia um captcha de imagem para cada novo usuário que entra ' \
            'no grupo e expulsa aquele que não enviar o captcha no tempo definido.\n' \
            '\n' \
            'Se um usuário tentar entrar no grupo 5 vezes sem enviar o captcha corretamente, vou ' \
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
            '- Se um usuário tentar entrar no grupo 5 vezes sem enviar o captcha corretamente, ' \
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
            'usando a opção /captcha_mode.'
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
            '/language ca\n' \
            '/language gl\n' \
            '/language zh_cn',

        'LANG_BAD_LANG' : \
            'Idioma inválido. Os idiomas disponíveis são Inglês, Espanhol, Catalão, ' \
            'Galego, Português (Brasil) e chinês. Defina um deles usando "en", "es", "ca", ' \
            '"gl", "pt_br" ou "zh_cn".\n' \
            '\n' \
            'Exemplos:\n' \
            '/language en\n' \
            '/language es\n' \
            '/language ca\n' \
            '/language gl\n' \
            '/language pt_br\n' \
            '/language zh_cn',

        'LANG_NOT_ARG' : \
            'O comando exige o idioma que será usado (en – inglês, es – espanhol, ' \
            'ca - catalão, gl - galego, pt_br – português (Brasil), zh_cn - chinês).\n' \
            '\n' \
            'Exemplos:\n' \
            '/language en\n' \
            '/language es\n' \
            '/language ca\n' \
            '/language gl\n' \
            '/language pt_br\n' \
            '/language zh_cn',

        'TIME_CHANGE' : \
            'Tempo para enviar o captcha modificado com sucesso para {} minutos.',

        'TIME_MAX_NOT_ALLOW' : \
            'O tempo máximo para resolver o captcha é de 120 minutos. Tempo não mudado.',

        'TIME_NOT_NUM' : \
            'O tempo fornecido não é um número integral.',

        'TIME_NOT_ARG' : \
            'O comando exige um valor para o tempo (em minutos).\n' \
            '\n' \
            'Exemplos:\n' \
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
            'Exemplos:\n' \
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
            'Exemplos:\n' \
            '/captcha_mode nums\n' \
            '/captcha_mode hex\n' \
            '/captcha_mode ascii',

        'CAPTCHA_MODE_NOT_ARG' : \
            'O comando exite um modo definido. As opções disponíveis são:\n' \
            '- Captchas numéricos ("nums").\n' \
            '- Captchas hexadecimais, com números e letras A-F ("hex").\n' \
            '- Captchas com números e letras A-Z ("ascii").\n' \
            '\n' \
            'Exemplos:\n' \
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
            'Alerta: Esta é a quinta vez que {} tenta entrar no grupo mas falha ao enviar o ' \
            'captcha. O "usuário" foi banido. Para deixá-lo entrar de novo, um administrador tem ' \
            'que remover as restrições, manualmente..',

        'NEW_USER_BAN_NOT_IN_CHAT' : \
            'Alerta: Esta é a quinta vez que {} tenta entrar no grupo mas falha ao enviar o ' \
            'captcha. Eu tentei banir o "usuário", mas ele não está mais no grupo (ele saiu ou ' \
            'foi expulso por um Admin).',

        'NEW_USER_BAN_NOT_RIGHTS' : \
            'Alerta: Esta é a quinta vez que {} tenta entrar no grupo mas falha ao enviar o ' \
            'captcha. Eu tentei banir o "usuário", mas eu não tenho poderes administrativos para ' \
            'banir usuários do grupo.',

        'BOT_CANT_BAN' : \
            'Alerta: Esta é a quinta vez que {} tenta entrar no grupo mas falha ao enviar o ' \
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
            'são: en (inglês) - es (espanhol) - ca (catalão) - gl (galego) - ' \
            'pt_br (português BR) - zh_cn (chinês).\n' \
            '\n' \
            '/time - Permite alterar o tempo disponível para resolver um captcha.\n' \
            '\n' \
            '/difficulty - Permite alterar o nível de dificuldade do captcha (de 1 a 5).\n' \
            '\n' \
            '/captcha_mode - Permite alterar o modo-carater do captcha (nums: apenas números, ' \
            'hex: números e letras A-F, ascii: números e letras A-Z).\n' \
            '\n' \
            '/enable - Ativa a proteção captcha no grupo.\n' \
            '\n' \
            '/disable - Desativa a proteção captcha no grupo.\n' \
            '\n' \
            '/version - Mostra a versão do Bot.\n' \
            '\n' \
            '/about - Mostra informações "sobre".'
    },
    'ZH_CN' : {
        'START' : \
            '你好，我是一个机器人通过发送图像验证码给刚加入群组中的每个新用户，' \
            '并踢出任何在时限内无法输入验证码的人。\n' \
            '\n' \
            '如果有人尝试加入群5次且没有输入验证码，我' \
            '将会认为这个用户是机器人，并且将他他拉黑。同样，任何' \
            '包含链接的消息在他输入验证码之前被发送，将会被' \
            '认为是垃圾信息并被删除。\n' \
            '\n' \
            '记得给我管理员权限以踢人和删除消息。\n' \
            '\n' \
            '检查 /help 命令以获取更多关于我的使用方法。\n' \
            '\n' \
            '我有用吗？检查 /about 命令并确认捐款给我使我保持运行。',

        'HELP' : \
            '机器人帮助:\n' \
            '————————————————\n' \
            '- 我是一个机器人通过发送图像验证码给刚加入群组中的每个新用户，并踢出任何' \
            '在时限内无法输入验证码的人。\n' \
            '\n' \
            '- 如果有人尝试加入群5次且没有输入验证码，' \
            '我将会认为这个用户是机器人，并且将他他拉黑。\n' \
            '\n' \
            '- 任何包含链接的消息在他输入验证码之前' \
            '被发送，将会被认为是垃圾信息并被删除。\n' \
            '\n' \
            '- 你需要给我管理员权限以踢人和删除消息。\n' \
            '\n' \
            '- 为了保持群组清洁, 我会删除与我有关的所有信息当' \
            '验证码没有输入和用户被踢出时（5分钟后）。\n' \
            '\n' \
            '- 用户在默认情况下必须在5分钟内输入验证码，但它' \
            '能通过 /time 命令被设置。\n' \
            '\n' \
            '- 你可以通关 /enable 和 /disable 命令设置验证码' \
            '的开启和关闭。\n' \
            '\n' \
            '- 设置类命令只能被群组管理员使用。\n' \
            '\n' \
            '- 你可以用 /language 命令设置我的语言。\n' \
            '\n' \
            '- 你可以通过 /difficulty 命令设置验证码难度。\n' \
            '\n' \
            '- 您可以将验证码设置为仅使用数字（默认）或完整数字和字母，' \
            '通过命令 /captcha_mode.\n' \
            '\n' \
            '- 检查 /commands 以获取可用命令列表，以及' \
            '它们的描述。',

        'CMD_NOT_ALLOW' : \
            '该命令只有管理员可以使用。',

        'LANG_CHANGE' : \
            '语言已设置为中文。',

        'LANG_SAME' : \
            '我已经被设置为中文。\n' \
            '\n' \
            '你是否需要使用以下命令:\n' \
            '/language en\n' \
            '/language es\n' \
            '/language ca\n' \
            '/language gl\n' \
            '/language pt_br',

        'LANG_BAD_LANG' : \
            '无此语言。目前支持英语，西班牙语，' \
            '加泰罗尼亚语，加利西亚，中文和葡萄牙语（巴西）。使用en - 英文，es - 西班牙语，' \
            'ca - 加泰罗尼亚语，gl - 加利西亚, pt_br - 葡萄牙语（巴西），zh-CN - 中文。\n' \
            '\n' \
            '如:\n' \
            '/language en\n' \
            '/language es\n' \
            '/language ca\n' \
            '/language gl\n' \
            '/language pt_br\n' \
            '/language zh_cn',

        'LANG_NOT_ARG' : \
            '这个命令需要一个语言参数（en - 英文，es - 西班牙语，ca - 加泰罗尼亚语，' \
            'gl - 加利西亚，pt_br - 葡萄牙语（巴西）），zh-CN - 中文。\n' \
            '\n' \
            '如:\n' \
            '/language en\n' \
            '/language es\n' \
            '/language ca\n' \
            '/language gl\n' \
            '/language pt_br\n' \
            '/language zh_cn',

        'TIME_CHANGE' : \
            '输入验证码的时间成功设置为 {} 分钟。',

        'TIME_MAX_NOT_ALLOW' : \
            '允许的验证码最大输入时间为120分钟，或，时间没有改变。',

        'TIME_NOT_NUM' : \
            '提供的时间不是整数。',

        'TIME_NOT_ARG' : \
            '该命令需要设置时间值（以分钟为单位）。\n' \
            '\n' \
            '如:\n' \
            '/time 3\n' \
            '/time 5\n' \
            '/time 10',

        'DIFFICULTY_CHANGE' : \
            '验证码难度成功更改为级别 {}。',

        'DIFFICULTY_NOT_NUM' : \
            '提供的验证码难度不是数字。',

        'DIFFICULTY_NOT_ARG' : \
            '该命令需要设置难度级别（从1到5）。\n' \
            '\n' \
            '如:\n' \
            '/difficulty 1\n' \
            '/difficulty 2\n' \
            '/difficulty 3\n' \
            '/difficulty 4\n' \
            '/difficulty 5',

        'CAPTCHA_MODE_CHANGE' : \
            '验证码字符模式已成功更改为"{}"。',

        'CAPTCHA_MODE_INVALID' : \
            '验证码字符模式无效。 支持的模式有："nums" - 数字，"hex" - 十六进制可表示数值，和' \
            '"ascii" - 数字、英文组合。\n' \
            '\n' \
            '如:\n' \
            '/captcha_mode nums\n' \
            '/captcha_mode hex\n' \
            '/captcha_mode ascii',

        'CAPTCHA_MODE_NOT_ARG' : \
            '该命令需要设置字符模式。 可用的模式有：\n' \
            '- "nums" - 数字。\n' \
            '- "hex" - 十六进制可表示数值。\n' \
            '- "ascii" - 数字、英文组合。\n' \
            '\n' \
            '如:\n' \
            '/captcha_mode nums\n' \
            '/captcha_mode hex\n' \
            '/captcha_mode ascii',

        'NEW_USER_CAPTCHA_CAPTION' : \
            '你好 {}, 欢迎来到 {}, 请发送一条消息，其中包含此验证码' \
            '以验证你是人类。如果你没有在 {} ' \
            '分钟内输入验证码，你将会被自动踢出群组。',

        'CAPTHA_SOLVED' : \
            '验证码已输入，用户已验证。欢迎加入群组 {}',

        'CAPTCHA_INCORRECT_0' : \
            '这不是正确的数字。请再试一次。',

        'CAPTCHA_INCORRECT_1' : \
            '这不是正确的数字。请仔细检查，验证码有4个数字。',

        'NEW_USER_KICK' : \
            '{} 还没有及时完成验证码。“用户”已被踢出。',

        'NEW_USER_KICK_NOT_RIGHTS' : \
            '{} 还没有及时完成验证码。我试图踢出“用户”，但我' \
            '没有管理权限来踢出该群组中的用户。',

        'NEW_USER_KICK_NOT_IN_CHAT' : \
            '{} 还没有及时完成验证码。我试图踢出“用户”，但是' \
            '用户不在组中（已离开组或已被管理员踢出）。',

        'BOT_CANT_KICK' : \
            '{} 还没有及时完成验证码。我试图踢出“用户”，但因为' \
            '未知原因（可能与网络/服务器有关），我无法完成请求。',

        'CANT_DEL_MSG' : \
            '我试图删除此消息，但我没有管理权限以删除我尚未发送的消息。',

        'NEW_USER_BAN' : \
            '警告：这是 {} 尝试加入该组的第五次' \
            '输入验证码失败。“用户”被拉黑。为了让他/她再次进入，管理员必须' \
            '手动删除此“用户”的限制。',

        'NEW_USER_BAN_NOT_IN_CHAT' : \
            '警告：这是 {} 尝试加入该组的第五次' \
            '输入验证码失败。我试图拉黑“用户”，但用户已不在该群组。' \
            '（已离开组或已被管理员踢出）。',

        'NEW_USER_BAN_NOT_RIGHTS' : \
            '警告：这是 {} 尝试加入该组的第五次' \
            '输入验证码失败。我试图拉黑“用户”，但我没有管理权限以' \
            '拉黑此用户',

        'BOT_CANT_BAN' : \
            '警告：这是 {} 尝试加入该组的第五次' \
            '输入验证码失败。我试图拉黑“用户”，但因为' \
            '未知原因（可能与网络/服务器有关），我无法完成请求。',

        'SPAM_DETECTED_RM' : \
            '检测到来自 {} 的URL（或别名）的消息，该用户尚未输入' \
            '验证码。为了保持Telegram不被垃圾消息困扰，该消息已被删除' \
            ':)',

        'SPAM_DETECTED_NOT_RM' : \
            '检测到来自 {} 的URL（或别名）的消息，该用户尚未输入' \
            '验证码。我试图删除消息，但我没有管理权限以' \
            '删除消息',

        'NOT_TEXT_MSG_ALLOWED' : \
            '为了保持Telegram不被垃圾消息困扰，从 {} 中删除了非文本消息（图像，音频，文件...）' \
            '没有电子邮件的电报。\n' \
            '\n' \
            '输入验证码后，您可以发送非文本消息。',

        'OTHER_CAPTCHA_BTN_TEXT' : \
            '其他验证码',

        'ENABLE' : \
            '启用了验证码保护。 使用 /disable 命令禁用它。',

        'DISABLE' : \
            '禁用了验证码保护。 使用 /enable 命令启用它。',

        'ALREADY_ENABLE' : \
            '验证码保护已经启用。',

        'ALREADY_DISABLE' : \
            '验证码保护已经禁用。',

        'CAN_NOT_GET_ADMINS' : \
            '在当前聊天中无法使用此命令。',

        'VERSION' : \
            '当前机器人版本号： {}',

        'ABOUT_MSG' : \
            '这个机器人是免费软件，在GNU-GPL许可下开源。' \
            '开发者是 {}.\n' \
            '\n' \
            '你可以在这里查看源码：\n' \
            '{}\n' \
            '\n' \
            '你喜欢我的作品吗？请我杯咖啡吧。\n' \
            '\n' \
            'Paypal账号：\n' \
            '{}\n' \
            '\n' \
            'BTC型比特币地址：\n' \
            '{}',

        'COMMANDS' : \
            '命令列表：\n' \
            '————————————————\n' \
            '/start - 显示有关机器人的初始信息。\n' \
            '\n' \
            '/help - 显示帮助信息。\n' \
            '\n' \
            '/commands - 显示此消息。有关所有可用命令的信息和描述。\n' \
            '\n' \
            '/language - 更改机器人消息的语言。 目前' \
            '目前可用语言为： en - 英文，es - 西班牙语，ca - 加泰罗尼亚语，' \
            'gl - 加利西亚，zh-CN - 中文，pt_br - 葡萄牙语（巴西）。\n' \
            '\n' \
            '/time - 更改可用于输入验证码的时间。\n' \
            '\n' \
            '/difficulty - 更改验证码难度级别（从1到5）。\n' \
            '\n' \
            '/captcha_mode - 更改验证码字符模式（nums：数字，' \
            'hex：十六进制可表示数值，ascii：数字、英文组合。）\n' \
            '\n' \
            '/enable - 启用本群组验证码保护。\n' \
            '\n' \
            '/disable - 禁用本群组验证码保护。\n' \
            '\n' \
            '/version - 显示机器人版本号。\n' \
            '\n' \
            '/about - 显示“关于”信息。'
    }
}
