# -*- coding: utf-8 -*-

'''
Script:
    tlgbotutils.py
Description:
    Telegram Bot useful functions.
Author:
    Jose Miguel Rios Rubio
Creation date:
    02/11/2020
Last modified date:
    28/12/2022
Version:
    1.1.6
'''

###############################################################################
# Standard Libraries
###############################################################################

# Logging Library
import logging

# Date and Time Library
from datetime import datetime

# Data Types Library
from typing import List, Optional, Union


###############################################################################
# Third-Party Libraries
###############################################################################

# Python-Telegram_Bot Core Library
from telegram import (
    Bot, CallbackQuery, ChatMember, ChatMemberUpdated, ChatPermissions,
    InlineKeyboardMarkup, InputMedia, Message, ParseMode, PhotoSize, Poll,
    ReplyMarkup, TelegramError, Update, User
)

# Python-Telegram_Bot Utilities Library
from telegram.utils.helpers import DEFAULT_NONE

# Python-Telegram_Bot Data Types Library
from telegram.utils.types import (
    DVInput, FileInput, ODVInput
)


###############################################################################
# Local Libraries
###############################################################################

# Local Commons Library
from commons import add_lrm


###############################################################################
# Logger Setup
###############################################################################

logger = logging.getLogger(__name__)


###############################################################################
# Specific Telegram constants
###############################################################################

ANONYMOUS_ADMIN_ID = 1087968824


###############################################################################
# Functions
###############################################################################

def tlg_get_chat(
        bot: Bot,
        chat_id_or_alias: Union[str, int],
        timeout: ODVInput[float] = DEFAULT_NONE
        ):
    '''Telegram get chat data.'''
    chat_result: dict = {}
    chat_result["chat_data"] = None
    chat_result["error"] = ""
    # Add @ if alias was provided
    if isinstance(chat_id_or_alias, str):
        if chat_id_or_alias[0] != "@":
            chat_id_or_alias = f"@{chat_id_or_alias}"
    # Get Chat Data
    try:
        chat_result["chat_data"] = bot.get_chat(
            chat_id=chat_id_or_alias, timeout=timeout)
    except Exception as error:
        chat_result["error"] = str(error)
        logger.error("[%s] %s", chat_id_or_alias, str(error))
    return chat_result


def tlg_get_chat_member(
        bot: Bot,
        chat_id: Union[str, int],
        user_id: Union[str, int],
        timeout: ODVInput[float] = DEFAULT_NONE
        ):
    '''Telegram Get Chat member info.'''
    result: dict = {}
    result["member"] = None
    result["error"] = ""
    try:
        result["member"] = bot.get_chat_member(
            chat_id=chat_id, user_id=user_id, timeout=timeout)
    except Exception as error:
        result["error"] = str(error)
        logger.error("[%s] %s", chat_id, str(error))
    return result


def tlg_get_chat_members_count(
        bot: Bot,
        chat_id: Union[str, int],
        timeout: ODVInput[float] = DEFAULT_NONE
        ):
    '''telegram Get number of members in a Chat.'''
    result: dict = {}
    result["num_members"] = None
    result["error"] = ""
    try:
        result["num_members"] = bot.get_chat_member_count(
            chat_id=chat_id, timeout=timeout)
    except Exception as error:
        result["error"] = str(error)
        logger.error("[%s] %s", chat_id, str(error))
    return result


def tlg_get_msg_topic(msg: Message):
    '''Check and get Topic ID from a received message.'''
    if not msg.is_topic_message:
        return None
    return msg.message_thread_id


def tlg_send_msg(
        bot: Bot,
        chat_id: Union[str, int],
        text: str,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        disable_web_page_preview: ODVInput[bool] = DEFAULT_NONE,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[ReplyMarkup] = None,
        topic_id: Optional[int] = None,
        timeout: ODVInput[float] = DEFAULT_NONE
        ):
    '''Bot try to send a text message.'''
    sent_result: dict = {}
    sent_result["msg"] = None
    sent_result["error"] = ""
    if parse_mode == "HTML":
        parse_mode = ParseMode.HTML
    elif parse_mode == "MARKDOWN":
        parse_mode = ParseMode.MARKDOWN_V2
    try:
        sent_result["msg"] = bot.send_message(
                chat_id=chat_id, text=text, parse_mode=parse_mode,
                reply_markup=reply_markup,
                disable_web_page_preview=disable_web_page_preview,
                disable_notification=disable_notification,
                reply_to_message_id=reply_to_message_id,
                message_thread_id=topic_id, timeout=timeout)
        logger.debug(
                "[%s] TLG text msg %s sent",
                chat_id, sent_result["msg"]["message_id"])
    except TelegramError as error:
        sent_result["error"] = str(error)
        logger.error("[%s] %s", chat_id, str(error))
    return sent_result


def tlg_send_image(
        bot: Bot,
        chat_id: Union[int, str],
        photo: Union[FileInput, PhotoSize],
        caption: Optional[str] = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[ReplyMarkup] = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        topic_id: Optional[int] = None,
        timeout: DVInput[float] = 40,
        **kwargs
        ):
    '''Bot try to send an image message.'''
    sent_result: dict = {}
    sent_result["msg"] = None
    sent_result["error"] = ""
    try:
        sent_result["msg"] = bot.send_photo(
                chat_id=chat_id, photo=photo, caption=caption,
                disable_notification=disable_notification,
                reply_to_message_id=reply_to_message_id,
                reply_markup=reply_markup, parse_mode=parse_mode,
                message_thread_id=topic_id, timeout=timeout, **kwargs)
        logger.debug(
                "[%s] TLG image msg %s sent",
                chat_id, sent_result["msg"]["message_id"])
    except TelegramError as error:
        sent_result["error"] = str(error)
        logger.error("[%s] %s", chat_id, str(error))
    return sent_result


def tlg_send_poll(
        bot: Bot,
        chat_id: Union[int, str],
        question: str,
        options: List[str],
        correct_option_id: Optional[int] = None,
        open_period: Optional[int] = None,
        is_anonymous: bool = True,
        poll_type: str = Poll.REGULAR,  # pylint: disable=W0622
        explanation: Optional[str] = None,
        allows_multiple_answers: bool = False,
        is_closed: Optional[bool] = None,
        disable_notification: ODVInput[bool] = True,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[ReplyMarkup] = None,
        explanation_parse_mode: ODVInput[str] = DEFAULT_NONE,
        close_date: Optional[Union[int, datetime]] = None,
        topic_id: Optional[int] = None,
        timeout: ODVInput[float] = 40,
        **kwargs
        ):
    '''Bot try to send a Poll message'''
    sent_result: dict = {}
    sent_result["msg"] = None
    sent_result["error"] = ""
    try:
        msg = bot.send_poll(
                chat_id=chat_id, question=question, options=options,
                is_anonymous=is_anonymous, type=poll_type,
                allows_multiple_answers=allows_multiple_answers,
                correct_option_id=correct_option_id, is_closed=is_closed,
                disable_notification=disable_notification,
                reply_to_message_id=reply_to_message_id,
                reply_markup=reply_markup, message_thread_id=topic_id,
                timeout=timeout, explanation=explanation,
                explanation_parse_mode=explanation_parse_mode,
                open_period=open_period, close_date=close_date, **kwargs)
        logger.debug("[%s] TLG poll msg %d sent", chat_id, msg.message_id)
        sent_result["msg"] = msg
    except TelegramError as error:
        sent_result["error"] = str(error)
        logger.error("[%s] %s", chat_id, str(error))
    return sent_result


def tlg_stop_poll(
        bot: Bot,
        chat_id: Union[int, str],
        message_id: int,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        **kwargs
        ):
    '''Bot try to stop a Poll.'''
    result: dict = {}
    result["msg"] = None
    result["error"] = ""
    try:
        result["msg"] = bot.stop_poll(
                chat_id=chat_id, message_id=message_id,
                reply_markup=reply_markup, timeout=timeout, **kwargs)
        logger.debug("[%s] TLG poll %s stop", chat_id, message_id)
    except Exception as error:
        result["error"] = str(error)
        logger.error("[%s] %s", chat_id, str(error))
    return result


def tlg_delete_msg(
        bot: Bot,
        chat_id: Union[int, str],
        msg_id: int,
        timeout: ODVInput[float] = DEFAULT_NONE,
        ):
    '''Try to remove a telegram message'''
    delete_result: dict = {}
    delete_result["error"] = ""
    if msg_id is not None:
        logger.debug("[%s] TLG deleting msg %s", chat_id, msg_id)
        try:
            bot.delete_message(
                    chat_id=chat_id, message_id=msg_id, timeout=timeout)
            logger.debug("[%s] TLG msg %s deleted", chat_id, msg_id)
        except Exception as error:
            delete_result["error"] = str(error)
            logger.error("[%s] %s", chat_id, delete_result["error"])
    return delete_result


def tlg_edit_msg_media(
        bot: Bot,
        chat_id: Union[int, str],
        msg_id: int,
        inline_msg_id: Optional[int] = None,
        media: Optional[InputMedia] = None,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        ):
    '''Try to edit a telegram multimedia message'''
    edit_result: dict = {}
    edit_result["error"] = ""
    try:
        bot.edit_message_media(
                chat_id=chat_id, message_id=msg_id,
                inline_message_id=inline_msg_id, media=media,
                reply_markup=reply_markup, timeout=timeout)
    except Exception as error:
        edit_result["error"] = str(error)
        logger.error("[%s] %s", chat_id, str(error))
    return edit_result


def tlg_answer_callback_query(
        bot: Bot,
        query: CallbackQuery,
        text: Optional[str] = None,
        show_alert: bool = False,
        url: Optional[str] = None,
        cache_time: Optional[int] = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        ):
    '''Try to send a telegram callback query answer'''
    query_ans_result: dict = {}
    query_ans_result["error"] = ""
    try:
        bot.answer_callback_query(
                callback_query_id=query.id, text=text, show_alert=show_alert,
                url=url, cache_time=cache_time, timeout=timeout)
    except Exception as error:
        query_ans_result["error"] = str(error)
        logger.error("[%s] %s", query.message.chat_id, str(error))
    return query_ans_result


def tlg_ban_user(
        bot: Bot,
        chat_id: Union[str, int],
        user_id: Union[str, int],
        until_date: Optional[Union[int, datetime]] = None,
        timeout: ODVInput[float] = DEFAULT_NONE
        ):
    '''Telegram Ban a user of an specified chat'''
    ban_result: dict = {}
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
        bot.ban_chat_member(
                chat_id=chat_id, user_id=user_id, timeout=timeout,
                until_date=until_date)
    except Exception as error:
        ban_result["error"] = str(error)
        logger.error("[%s] %s", chat_id, str(error))
    return ban_result


def tlg_kick_user(
        bot: Bot,
        chat_id: Union[str, int],
        user_id: Union[str, int],
        timeout: ODVInput[float] = DEFAULT_NONE
        ):
    '''Telegram Kick a user of an specified chat'''
    kick_result: dict = {}
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
    # Kick User (remove restrictions with only_if_banned=False make
    # it kick)
    try:
        bot.unban_chat_member(
                chat_id=chat_id, user_id=user_id, timeout=timeout,
                only_if_banned=False)
    except Exception as error:
        kick_result["error"] = str(error)
        logger.error("[%s] %s", chat_id, str(error))
    return kick_result


def tlg_leave_chat(
        bot: Bot,
        chat_id: Union[str, int],
        timeout: ODVInput[float] = DEFAULT_NONE
        ):
    '''Telegram Bot try to leave a chat.'''
    left = False
    try:
        if bot.leave_chat(chat_id=chat_id, timeout=timeout):
            left = True
    except Exception as error:
        logger.error("[%s] %s", chat_id, str(error))
    return left


def tlg_restrict_user(
        bot: Bot,
        chat_id: Union[str, int],
        user_id: Union[str, int],
        send_msg: bool,
        send_media: bool,
        send_polls: bool,
        send_stickers_gifs: bool,
        insert_links: bool,
        change_group_info: bool,
        invite_members: bool,
        pin_messages: bool,
        manage_topics: bool,
        until_date: Optional[Union[int, datetime]] = None,
        timeout: ODVInput[float] = DEFAULT_NONE
        ):
    '''Telegram Bot try to restrict user permissions in a group.'''
    result = False
    try:
        permissions = ChatPermissions(
                send_msg, send_media, send_polls, send_stickers_gifs,
                insert_links, change_group_info, invite_members, pin_messages,
                manage_topics)
        result = bot.restrict_chat_member(
                chat_id=chat_id, user_id=user_id, permissions=permissions,
                until_date=until_date, timeout=timeout)
    except Exception as error:
        logger.error("[%s] %s", chat_id, str(error))
        result = False
    return result


def tlg_unrestrict_user(
        bot: Bot,
        chat_id: Union[str, int],
        user_id: Union[str, int],
        timeout: ODVInput[float] = DEFAULT_NONE
        ):
    '''Telegram Bot try to remove all user restrictions in a group.'''
    result = False
    try:
        permissions = ChatPermissions(
                True, True, True, True, True, True, True, True)
        result = bot.restrict_chat_member(
                chat_id=chat_id, user_id=user_id, permissions=permissions,
                timeout=timeout)
    except Exception as error:
        logger.error("[%s] %s", chat_id, str(error))
        result = False
    return result


def tlg_user_is_admin(
        bot: Bot,
        chat_id: Union[str, int],
        user_id: Union[str, int],
        timeout: ODVInput[float] = DEFAULT_NONE
        ):
    '''Check if the specified user is an Administrator of a group given
    by IDs'''
    # Check if it is an Admin with anonymous config enabled
    if user_id == ANONYMOUS_ADMIN_ID:
        return True
    # Get group Admins
    try:
        group_admins = bot.get_chat_administrators(
                chat_id=chat_id, timeout=timeout)
    except Exception as error:
        logger.error("[%s] %s", chat_id, str(error))
        return None
    # Check if the user is one of the group Admins
    for admin in group_admins:
        if user_id == admin.user.id:
            return True
    return False


def tlg_is_a_channel_msg_on_discussion_group(msg: Message):
    '''Check if a Telegram message is a channel publish send to linked
    discussion group of that group.'''
    is_automatic_forward = getattr(msg, "is_automatic_forward", None)
    return is_automatic_forward


def tlg_get_chat_type(
        bot: Bot,
        chat_id_or_alias: Union[str, int],
        timeout: ODVInput[float] = DEFAULT_NONE
        ):
    '''
    Telegram check if a chat exists and what type it is (user, group,
    channel).
    '''
    chat_type = None
    chat_result = tlg_get_chat(bot, chat_id_or_alias, timeout)
    if chat_result["chat_data"] is not None:
        chat_type = getattr(chat_result["chat_data"], "type", None)
    return chat_type


def tlg_is_valid_user_id_or_alias(user_id_alias: Union[str, int]):
    '''
    Check if given telegram ID or alias has a valid expected format.
    '''
    # Check if it is a valid alias (start with @ and have 5 characters
    # or more)
    if isinstance(user_id_alias, str):
        if (user_id_alias[0] == "@") and (len(user_id_alias) > 5):
            return True
    # Check if it is a valid ID (is a number larger than 0)
    try:
        user_id = int(user_id_alias)
        if user_id > 0:
            return True
    except ValueError:
        return False
    return False


def tlg_is_valid_group(group: Union[str, int]):
    '''Check if given telegram Group ID has a valid expected format.'''
    # Check if it start with '-'
    if isinstance(group, str):
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


def tlg_alias_in_string(str_text: str):
    ''' Check if a string contains an alias.'''
    for word in str_text.split():
        if (len(word) > 1) and (word[0] == '@'):
            return True
    return False


def tlg_extract_members_status_change(chat_member_update: ChatMemberUpdated):
    '''
    Takes a ChatMemberUpdated instance and extracts whether the
    "old_chat_member" was a member of the chat and whether the
    "new_chat_member" is a member of the chat. Returns None, if the
    status didn't change.'''
    status_change = chat_member_update.difference().get("status")
    old_is_member, new_is_member = chat_member_update.difference().get(
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


def tlg_get_user_name(user: User, truncate_name_len: int = 0):
    '''
    Get and return a Telegram member username. It allows to truncate the
    name if argument for that ar provided. It applies a LRM mark to
    ensure and fix any possible representation error due Right-To-Left
    language texts.
    '''
    user_name = ""
    if user is None:
        return "None"
    if user.name is not None:
        user_name = user.name
    else:
        user_name = user.full_name
    # If the user name is too long, truncate it to specified num of
    # characters
    if truncate_name_len > 0:
        if len(user_name) > truncate_name_len:
            user_name = user_name[0:truncate_name_len]
    # Add an unicode Left to Right Mark (LRM) to user name (names fix
    # for arabic, hebrew, etc.)
    user_name = add_lrm(user_name)
    return user_name


def tlg_has_new_member_join_group(chat_member: ChatMemberUpdated):
    '''
    Check chat members status changes and detect if the provided member
    has join the current group.
    '''
    # Check members changes
    result = tlg_extract_members_status_change(chat_member)
    if result is None:
        return False
    was_member, is_member = result
    # Check if it is a new member join
    if was_member:
        return False
    if not is_member:
        return False
    return True


def tlg_get_msg(update: Update):
    '''Get Telegram message data from the Update element.'''
    msg = getattr(update, "message", None)
    if msg is None:
        msg = getattr(update, "edited_message", None)
    if msg is None:
        msg = getattr(update, "channel_post", None)
    return msg
