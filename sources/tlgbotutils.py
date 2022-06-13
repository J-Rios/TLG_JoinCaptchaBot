# -*- coding: utf-8 -*-

'''
Script:
    tlgbotutils.py
Description:
    Telegram Bot useful functions
Author:
    Jose Miguel Rios Rubio
Creation date:
    02/11/2020
Last modified date:
    13/06/2022
Version:
    1.1.4
'''

###############################################################################
### Imported modules

from typing import Tuple, Optional

from telegram import (
    ChatPermissions, TelegramError, ParseMode, Poll, ChatMemberUpdated,
    ChatMember
)

from telegram.utils.helpers import DEFAULT_NONE

from commons import printts

###############################################################################
### Specific Telegram constants

ANONYMOUS_ADMIN_ID = 1087968824

###############################################################################
### Functions

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


def tlg_get_chat_members_count(bot, chat_id, timeout=None):
    '''telegram Get number of members in a Chat.'''
    result = dict()
    result["num_members"] = None
    result["error"] = ""
    try:
        result["num_members"] = bot.get_chat_member_count(chat_id=chat_id,
            timeout=timeout)
    except Exception as e:
        result["error"] = str(e)
        printts("[{}] {}".format(chat_id, result["error"]))
    return result


def tlg_send_msg(bot, chat_id, text, parse_mode=None,
    disable_web_page_preview=None, disable_notification=True,
    reply_to_message_id=None, reply_markup=None, timeout=None):
    '''Bot try to send a text message'''
    sent_result = dict()
    sent_result["msg"] = None
    sent_result["error"] = ""
    if parse_mode == "HTML":
        parse_mode = ParseMode.HTML
    elif parse_mode == "MARKDOWN":
        parse_mode = ParseMode.MARKDOWN_V2
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
    disable_notification=True, reply_to_message_id=None,
    reply_markup=None, timeout=40, parse_mode=None):
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


def tlg_send_poll(bot, chat_id, question, options, correct_option_id=None,
                  open_period=None, is_anonymous=True, type=Poll.REGULAR,
                  explanation=None, allows_multiple_answers=False,
                  is_closed=None, disable_notification=True,
                  reply_to_message_id=None, reply_markup=None,
                  explanation_parse_mode=DEFAULT_NONE, close_date=None,
                  timeout=40, **kwargs):
    '''Bot try to send a Poll message'''
    sent_result = dict()
    sent_result["msg"] = None
    sent_result["error"] = ""
    try:
        sent_result["msg"] = bot.send_poll(chat_id=chat_id, question=question,
            options=options, is_anonymous=is_anonymous, type=type,
            allows_multiple_answers=allows_multiple_answers,
            correct_option_id=correct_option_id, is_closed=is_closed,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id, reply_markup=reply_markup,
            timeout=timeout, explanation=explanation,
            explanation_parse_mode=explanation_parse_mode,
            open_period=open_period, close_date=close_date, **kwargs)
    except TelegramError as e:
        sent_result["error"] = str(e)
        printts("[{}] {}".format(chat_id, sent_result["error"]))
    return sent_result


def tlg_stop_poll(bot, chat_id, message_id, reply_markup=None,
                  timeout=None, **kwargs):
    '''Bot try to stop a Poll.'''
    result = dict()
    result["msg"] = None
    result["error"] = ""
    try:
        result["msg"] = bot.stop_poll(chat_id=chat_id, message_id=message_id,
            reply_markup=reply_markup, timeout=timeout, **kwargs)
    except Exception as e:
            result["error"] = str(e)
            printts("[{}] {}".format(chat_id, result["error"]))
    return result


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
    # Ban User
    try:
        bot.ban_chat_member(chat_id=chat_id, user_id=user_id,
            timeout=timeout, until_date=until_date)
    except Exception as e:
        ban_result["error"] = str(e)
        printts("[{}] {}".format(chat_id, ban_result["error"]))
    return ban_result


def tlg_kick_user(bot, chat_id, user_id, timeout=None):
    '''Telegram Kick a user of an specified chat'''
    kick_result = dict()
    kick_result["error"] = ""
    # Get chat member info
    # Do nothing if user left the group or has been kick/ban by an Admin
    member_info_result = tlg_get_chat_member(bot, chat_id, user_id)
    if member_info_result["member"] is None:
        kick_result["error"] = member_info_result["error"]
        return kick_result
    if member_info_result["member"]["status"] == "left":
        kick_result["error"] = "The user has left the group"
        return kick_result
    if member_info_result["member"]["status"] == "kicked":
        kick_result["error"] = "The user was already kicked"
        return kick_result
    # Kick User (remove restrictions with only_if_banned=False make it kick)
    try:
        bot.unban_chat_member(chat_id=chat_id, user_id=user_id,
            timeout=timeout, only_if_banned=False)
    except Exception as e:
        kick_result["error"] = str(e)
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
    # Check if it is an Admin with anonymous config enabled
    if user_id == ANONYMOUS_ADMIN_ID:
        return True
    # Get group Admins
    try:
        group_admins = bot.get_chat_administrators(chat_id=chat_id,
            timeout=timeout)
    except Exception as e:
        printts("[{}] {}".format(chat_id, str(e)))
        return None
    # Check if the user is one of the group Admins
    for admin in group_admins:
        if user_id == admin.user.id:
            return True
    return False


def tlg_is_a_channel_msg_on_discussion_group(msg):
    '''Check if a Telegram message is a channel publish send to linked
    discussion group of that group.'''
    is_automatic_forward = getattr(msg, "is_automatic_forward", None)
    return is_automatic_forward


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
    # Check if it is a valid alias (start with @ and have 5 characters or more)
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


def tlg_alias_in_string(str_text):
    ''' Check if a string contains an alias.'''
    for word in str_text.split():
        if (len(word) > 1) and (word[0] == '@'):
            return True
    return False


def tlg_extract_members_status_change(
    chat_member_update: ChatMemberUpdated,
) -> Optional[Tuple[bool, bool]]:
    '''Takes a ChatMemberUpdated instance and extracts whether the
    "old_chat_member" was a member of the chat and whether the
    "new_chat_member" is a member of the chat. Returns None, if the status
    didn't change.'''
    status_change = chat_member_update.difference().get("status")
    old_is_member, new_is_member = chat_member_update.difference().get( \
            "is_member", (None, None))
    if status_change is None:
        if (old_is_member is None) or (new_is_member is None):
            return None
        was_member = old_is_member
        is_member = new_is_member
        return was_member, is_member
    old_status, new_status = status_change
    was_member = old_status in [
        ChatMember.MEMBER,
        ChatMember.CREATOR,
        ChatMember.ADMINISTRATOR,
    ] or (old_status == ChatMember.RESTRICTED and old_is_member is True)
    is_member = new_status in [
        ChatMember.MEMBER,
        ChatMember.CREATOR,
        ChatMember.ADMINISTRATOR,
    ] or (new_status == ChatMember.RESTRICTED and new_is_member is True)
    return was_member, is_member
