# -*- coding: utf-8 -*-

'''
Script:
    tlgbotutils.py
Description:
    Telegram Bot useful functions
Author:
    Jose Rios Rubio
Creation date:
    02/11/2020
Last modified date:
    03/11/2020
Version:
    1.0.0
'''

###############################################################################
### Imported modules

from telegram import ChatPermissions
from telegram import TelegramError

from commons import printts

###############################################################################

def tlg_get_chat(bot, chat_id_or_alias, timeout=None):
    '''Telegram get chat data.'''
    chat_result = dict()
    chat_result["chat_data"] = None
    chat_result["error"] = ""
    try:
        chat_result["chat_data"] = bot.get_chat(chat_id=chat_id_or_alias,
            timeout=timeout)
    except Exception as e:
        chat_result["error"] = str(e)
        printts("[{}] {}".format(chat_id_or_alias, chat_result["error"]))
    return chat_result


def tlg_get_chat_member(bot, chat_id, user_id, timeout=None):
    '''telegram Get Chat member info.'''
    result = dict()
    result["member"] = None
    result["error"] = ""
    try:
        result["member"] = bot.get_chat_member(chat_id=chat_id,
            user_id=user_id, timeout=timeout)
    except Exception as e:
        result["error"] = str(e)
        printts("[{}] {}".format(chat_id, result["error"]))
    return result


def tlg_send_msg(bot, chat_id, text, parse_mode=None,
    disable_web_page_preview=None, disable_notification=False,
    reply_to_message_id=None, reply_markup=None, timeout=None):
    '''Bot try to send a text message'''
    sent_result = dict()
    sent_result["msg"] = None
    sent_result["error"] = ""
    try:
        sent_result["msg"] = bot.send_message(chat_id=chat_id, text=text,
            parse_mode=parse_mode, reply_markup=reply_markup,
            disable_web_page_preview=disable_web_page_preview,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id, timeout=timeout)
    except TelegramError as e:
        sent_result["error"] = str(e)
        printts("[{}] {}".format(chat_id, sent_result["error"]))
    return sent_result


def tlg_send_image(bot, chat_id, photo, caption=None,
    disable_notification=False, reply_to_message_id=None,
    reply_markup=None, timeout=20, parse_mode=None):
    '''Bot try to send an image message'''
    sent_result = dict()
    sent_result["msg"] = None
    sent_result["error"] = ""
    try:
        sent_result["msg"] = bot.send_photo(chat_id=chat_id, photo=photo,
            caption=caption, disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id, reply_markup=reply_markup,
            timeout=timeout, parse_mode=parse_mode)
    except TelegramError as e:
        sent_result["error"] = str(e)
        printts("[{}] {}".format(chat_id, sent_result["error"]))
    return sent_result


def tlg_delete_msg(bot, chat_id, msg_id, timeout=None):
    '''Try to remove a telegram message'''
    delete_result = dict()
    delete_result["error"] = ""
    if msg_id is not None:
        try:
            bot.delete_message(chat_id=chat_id, message_id=msg_id,
                timeout=timeout)
        except Exception as e:
            delete_result["error"] = str(e)
            printts("[{}] {}".format(chat_id, delete_result["error"]))
    return delete_result


def tlg_edit_msg_media(bot, chat_id, msg_id, inline_msg_id=None,
    media=None, reply_markup=None, timeout=None):
    '''Try to edit a telegram multimedia message'''
    edit_result = dict()
    edit_result["error"] = ""
    try:
        bot.edit_message_media(chat_id=chat_id, message_id=msg_id,
            inline_message_id=inline_msg_id, media=media,
            reply_markup=reply_markup, timeout=timeout)
    except Exception as e:
        edit_result["error"] = str(e)
        printts("[{}] {}".format(chat_id, edit_result["error"]))
    return edit_result


def tlg_answer_callback_query(bot, query, text=None, show_alert=False,
    url=None, cache_time=None, timeout=None):
    '''Try to send a telegram callback query answer'''
    query_ans_result = dict()
    query_ans_result["error"] = ""
    try:
        bot.answer_callback_query(callback_query_id=query.id, text=text,
            show_alert=show_alert, url=url, cache_time=cache_time,
            timeout=timeout)
    except Exception as e:
        query_ans_result["error"] = str(e)
        printts("[{}] {}".format(query.message.chat_id, str(e)))
    return query_ans_result


def tlg_ban_user(bot, chat_id, user_id, timeout=None, until_date=None):
    '''Telegram Ban a user of an specified chat'''
    ban_result = dict()
    ban_result["error"] = ""
    # Get chat member info
    member_info_result = tlg_get_chat_member(bot, chat_id, user_id)
    if member_info_result["member"] is None:
        ban_result["error"] = member_info_result["error"]
        return ban_result
    # Check if user is not in the group
    if member_info_result["member"]["status"] == "left":
        ban_result["error"] = "The user has left the group"
        return ban_result
    if member_info_result["member"]["status"] == "kicked":
        ban_result["error"] = "The user was already kicked"
        return ban_result
    # Kick the user
    try:
        bot.kick_chat_member(chat_id=chat_id, user_id=user_id,
            timeout=timeout, until_date=until_date)
    except Exception as e:
        ban_result["error"] = str(e)
        printts("[{}] {}".format(chat_id, ban_result["error"]))
    return ban_result


def tlg_kick_user(bot, chat_id, user_id, timeout=None):
    '''Telegram Kick a user of an specified chat'''
    kick_result = dict()
    kick_result["error"] = ""
    # Ban the user (telegram doesn't have a kick method, so we need first
    # to ban and then remove ban restrictions of the user
    kick_result = tlg_ban_user(bot, chat_id, user_id)
    try:
        bot.unban_chat_member(chat_id=chat_id, user_id=user_id,
            timeout=timeout)
    except Exception as e:
        printts("[{}] {}".format(chat_id, str(e)))
    return kick_result


def tlg_leave_chat(bot, chat_id, timeout=None):
    '''Telegram Bot try to leave a chat.'''
    left = False
    try:
        if bot.leave_chat(chat_id=chat_id, timeout=timeout):
            left = True
    except Exception as e:
        printts("[{}] {}".format(chat_id, str(e)))
    return left


def tlg_restrict_user(bot, chat_id, user_id, until_date=None, timeout=None,
    send_msg=None, send_media=None, send_stickers_gifs=None,
    insert_links=None, send_polls=None, invite_members=None,
    pin_messages=None, change_group_info=None):
    '''Telegram Bot try to restrict user permissions in a group.'''
    result = False
    try:
        permissions = ChatPermissions(send_msg, send_media, send_polls,
            send_stickers_gifs, insert_links, change_group_info,
            invite_members, pin_messages)
        result = bot.restrict_chat_member(chat_id=chat_id, user_id=user_id,
            permissions=permissions, until_date=until_date, timeout=timeout)
    except Exception as e:
        printts("[{}] {}".format(chat_id, str(e)))
        result = False
    return result


def tlg_user_is_admin(bot, user_id, chat_id, timeout=None):
    '''Check if the specified user is an Administrator of a group given
    by IDs'''
    try:
        group_admins = bot.get_chat_administrators(chat_id=chat_id,
            timeout=timeout)
    except Exception as e:
        printts("[{}] {}".format(chat_id, str(e)))
        return None
    for admin in group_admins:
        if user_id == admin.user.id:
            return True
    return False


def tlg_get_chat_type(bot, chat_id_or_alias, timeout=None):
    '''Telegram check if a chat exists and what type it is (user, group, '''
    '''channel).'''
    chat_type = None
    chat_result = tlg_get_chat(bot, chat_id_or_alias, timeout)
    if chat_result["chat_data"] is not None:
        chat_type = getattr(chat_result["chat_data"], "type", None)
    return chat_type


def tlg_is_valid_user_id_or_alias(user_id_alias):
    '''Check if given telegram ID or alias has a valid expected format.'''
    # Check if it is a valid alias (start with a @ and have 5 characters or more)
    if user_id_alias[0] == '@':
        if len(user_id_alias) > 5:
            return True
    # Check if it is a valid ID (is a number larger than 0)
    try:
        user_id = int(user_id_alias)
        if user_id > 0:
            return True
    except ValueError:
        return False
    return False


def tlg_is_valid_group(group):
    '''Check if given telegram Group ID has a valid expected format.'''
    # Check if it start with '-'
    if group[0] != '-':
        return False
    # Check if it is a valid ID (is a number larger than 0)
    try:
        user_id = int(group)
    except ValueError:
        return False
    if user_id == 0:
        return False
    return True
