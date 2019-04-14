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
    14/04/2019
Version:
    1.2.5
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
    'F_TLDS' : 'tlds-alpha-by-domain.txt', # IANA TLD list (https://data.iana.org/TLD/tlds-alpha-by-domain.txt)
    'REGEX_URLS' : r'((?<=[^a-zA-Z0-9])*(?:https\:\/\/|[a-zA-Z0-9]{{1,}}\.{{1}}|\b)(?:\w{{1,}}\.{{1}}){{1,5}}(?:{})\b/?(?!@))',
    'DEVELOPER' : '@JoseTLG', # Bot developer
    'REPOSITORY' : 'https://github.com/J-Rios/TLG_JoinCaptchaBot', # Bot code repository
    'DEV_PAYPAL' : 'https://www.paypal.me/josrios', # Developer Paypal address
    'DEV_BTC' : '3N9wf3FunR6YNXonquBeWammaBZVzTXTyR', # Developer Bitcoin address
    'VERSION' : '1.2.5 (14/04/2019)' # Bot version
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
            '- Check /commands for get a list of all avaliable commands, and a short ' \
            'description of all of them.',

        'CMD_NOT_ALLOW' : \
            'Just an Admin can use this command',

        'LANG_CHANGE' : \
            'Language changed to english.',

        'LANG_SAME' : \
            'I am already in english.\n\nMay you want to say:\n/language es\n/language pt_br',

        'LANG_BAD_LANG' : \
            'Invalid language provided. The actual languages supported are english, spanish and ' \
            'portuguese (Brazil). Change any of them using "en" or "es".\n' \
            '\n' \
            'Example:\n' \
            '/language en\n' \
            '/language es\n' \
            '/language pt_br',

        'LANG_NOT_ARG' : \
            'The command needs a language to set (en - english, es - spanish, ' \
            'pt_br - portugese from Brazil).\n' \
            '\n' \
            'Example:\n' \
            '/language en\n' \
            '/language es\n' \
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

        'NEW_USER_CAPTCHA_CAPTION' : \
            'Hello {}, welcome to {}, please send a message with the number that appear in this ' \
            'captcha to verify that you are a human. If you don\'t resolve the captcha in {} ' \
            'mins, you will be automatically kick from the group.',

        'CAPTHA_SOLVED' : \
            'Captcha solved, user verified.\nWelcome to the group {}.',

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
            'Detected a message with an URL from {}, who has not solved the captcha yet. ' \
            'The message has been removed for the sake of a Telegram free of spam :)',

        'SPAM_DETECTED_NOT_RM' : \
            'Message with an URL detected from {}, who has not solved the captcha yet. ' \
            'I try to remove the Spam message, but I don\'t have the administration rights for ' \
            'remove messages that has not been sent by me.',

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
            'This is a free software and open-source GNU-GPL licensed Bot developed by the ' \
            'telegram user {}.\n\nYou can check the code here:\n{}\n\n' \
            'Do you like my work? Buy me a coffee.\n\nPaypal:\n{}\n\nBTC:\n{}',
       
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
            '- Echa un vistazo al comando /commands para ver una lista con todos los comandos ' \
            'disponibles y una breve descripción de cada uno de ellos.',

        'CMD_NOT_ALLOW' : \
            'Solo un Admin puede utilizar este comando.',

        'LANG_CHANGE' : \
            'Idioma cambiado a español.',

        'LANG_SAME' : \
            'Ya estoy en español.\n\nQuizás querías decir:\n/language en\n/language pt_br',

        'LANG_BAD_LANG' : \
            'Idioma inválidado. Los idiomas actualmente soportados son el inglés, el español y ' \
            'el portugués de Brasil. Cambia a uno de ellos mediante las etiquetas "en", "es" o ' \
            '"pt_br".\n' \
            '\n' \
            'Ejemplo:\n' \
            '/language en\n' \
            '/language es\n' \
            '/language pt_br',

        'LANG_NOT_ARG' : \
            'El comando necesita un idioma que establecer (en - inglés, es - español, ' \
            'pt_br - portugués de brasil).\n' \
            '\n' \
            'Ejemplo:\n' \
            '/language en\n' \
            '/language es\n' \
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

        'NEW_USER_CAPTCHA_CAPTION' : \
            'Hola {}, bienvenido a {}, por favor envía un mensaje con el número que aparece ' \
            'en esta imagen para verificar que eres un humano. Si no resuelves este captcha en ' \
            '{} mins, serás kickeado del grupo automáticamente.',

        'CAPTHA_SOLVED' : \
            'Captcha resuelto, usuario verificado.\nBienvenido al grupo {}.',

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
            'Se ha detectado un mensaje con URL enviado por {}, quien aún no ha resuelto el ' \
            'captcha. El mensaje ha sido eliminado en aras de un Telegram libre de Spam :)',

        'SPAM_DETECTED_NOT_RM' : \
            'Se ha detectado un mensaje con URL enviado por {}, quien aún no ha resuelto el ' \
            'captcha. He intentado borrar el mensaje, pero no se me han dado los privilegios de ' \
            'administración necesarios para eliminar mensajes que no son míos.',

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
            'el usuario de telegram {}.\n\nPuedes consultar el código aquí:\n{}\n\n' \
            'Te gusta lo que hago? Invítame a un café.\n\nPaypal:\n{}\n\nBTC:\n{}',

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
            'Confira o comando /help para saber mais sobre como me usar.',

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
            '- Use a opção /commands para ver a lista de todos os comandos com uma breve ' \
            'descrição de cada um deles.',

        'CMD_NOT_ALLOW' : \
            'Apenas um Admin pode usar esse comando',

        'LANG_CHANGE' : \
            'Idioma definido para Português (Brasil).',

        'LANG_SAME' : \
            'Eu já estou em Português (Brasil).\n\nQuem sabe você quer usar:\n' \
            '/language en\n' \
            '/language es',

        'LANG_BAD_LANG' : \
            'Idioma inválido. Os idiomas disponíveis são Inglês, Espanhol e Português (Brasil). ' \
            'Defina um deles usando "en", "es" ou "pt_br".\n' \
            '\n' \
            'Exemplo:\n' \
            '/language en\n' \
            '/language es\n' \
            '/language pt_br',

        'LANG_NOT_ARG' : \
            'O comando exige o idioma que será usado (en – Inglês, es – Espanhol, ' \
            'pt_br – Português (Brasil)).\n' \
            '\n' \
            'Exemplo:\n' \
            '/language en\n' \
            '/language es\n' \
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

        'NEW_USER_CAPTCHA_CAPTION' : \
            'Olá {}, seja bem-vindo ao {}. Por favor envie uma mensagem com o número que ' \
            'aparece neste captcha para que possamos nos certificar que você é humano. Se você ' \
            'não enviar o captcha em {} minutos, você será automaticamente expulso do grupo.',

        'CAPTHA_SOLVED' : \
            'Captcha enviado, usuário verificado.\nSeja bem-vindo ao grupo {}.',

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
            'Detectou uma mensagem com um URL de {}, que ainda não resolveu o captcha. ' \
            'A mensagem foi removida por causa de um Telegram livre de spam :)',

        'SPAM_DETECTED_NOT_RM' : \
            'Detectou uma mensagem com um URL de {}, que ainda não resolveu o captcha. ' \
            'Eu tentei apagar essa mensagem, mas eu não tenho poderes administrativos para ' \
            'remover mensagens que não foram enviadas por mim.',

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
            'Este é um Software Livre licenciado pela GNU-GPL Bot desenvolvido pelo usuário do ' \
            'Telegram {}.\n\nVocê pode acessar o código fonte aqui:\n{}\n\n' \
            'Gosta do meu trabalho? Me pague um café.\n\nPaypal:\n{}\n\nBTC:\n{}',

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
