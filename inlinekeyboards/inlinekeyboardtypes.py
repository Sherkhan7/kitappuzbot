from inlinekeyboards.inlinekeyboardvariables import *

inline_keyboard_types = {

    book_keyboard: [
        {
            "text_uz": "Kitob haqida",
            "emoji": "ℹ",
            "data": ""
        },
        {
            "text_uz": "Buyurtma qilish",
            "emoji": "🛍",
            "data": "ordering"
        },
        {
            "text_uz": "Ortga",
            "emoji": "«",
            "data": "back"
        },
    ],

    social_medias_keyboard: [
        {
            "text_uz": "Facebook",
            "emoji": "Ⓕ",
            "url": "https://www.facebook.com/kitappuz"
        },
        {
            "text_uz": "Instagram",
            "emoji": "Ⓘ",
            "url": "https://www.instagram.com/kitappuz/"
        },
        {
            "text_uz": "YouTube",
            "emoji": "Ⓨ",
            "url": "https://www.youtube.com/channel/UCFdIniiwJBAdd-Yoqk0bvwA"
        },
        {
            "text_uz": "TikTok",
            "emoji": "Ⓣ",
            "url": "https://vm.tiktok.com/ZSJuX1Tsr/"
        },
    ],

    confirm_keyboard: {
        "uz": ["Tasdiqlash", "Buyurtmani bekor qilish"],
        "cy": ["Тасдиқлаш", "Таҳрирлаш"],
        "ru": ["Подтвердить", "Редактировать"],
    },

    order_keyboard: {
        "uz": {1: "Buyurtma berish", 2: "Ortga"},
    },

    orders_keyboard: {
        "uz": {1: "Qabul qilish", 2: "Rad etish"},

    },

    yes_no_keyboard: {
        "uz": {1: "Ha", 2: "Yo'q"}
    },

    basket_keyboard: {
        "uz": {1: "Buyurtmani davom ettirish", 2: "Buyurtmani tasdiqlash"},
    },

    delivery_keyboard: {
        "uz": ["Yetkazib berildi"]
    },

}
