/* ==========================================
   CivicConnect - FAQ Chatbot Widget
   Self-contained: injects its own HTML + CSS.
   Just add <script src=".../chatbot.js"></script>
   before </body> on any page to enable it.
========================================== */

(function () {

    function initChatbot() {

    // ---------- Knowledge Base ----------
    // Each entry: keywords (any match triggers) + answer

    const faq = [
        {
            keywords: ["complaint kaise", "register complaint", "how to complain", "complaint kare", "complaint karna"],
            answer: "Complaint register karne ke liye: Login karo → 'Register Complaint' pe click karo → category, title, description, area aur ward bharo → Submit karo. Ward apne aap select ho jayega jab tum apna area type karoge."
        },
        {
            keywords: ["track", "status dekh", "complaint status", "mera complaint kaha"],
            answer: "Apni complaint track karne ke liye navbar mein 'Track' pe jao aur apna Complaint ID daalo. Wahan status (Pending / In Progress / Resolved / Rejected) dikh jayega."
        },
        {
            keywords: ["ward kaunsa", "mera ward", "which ward", "area kaunse ward"],
            answer: "CivicConnect Ward 11 aur Ward 12 (Degloor Naka, Nanded) cover karta hai. Ward 11: Islampura, Millat Nagar, Rehmat Nagar, Haider Bagh. Ward 12: Bhagwan Gali, Umar Colony, Khudbe Nagar, Pakiza Nagar. Poori list 'Wards' page pe hai."
        },
        {
            keywords: ["login", "password bhool", "forgot password", "account nahi"],
            answer: "Login karne ke liye apna email aur password daalo. Agar account nahi hai to 'Register' se naya account bana lo. Password bhool gaye ho to abhi reset feature available nahi hai, admin se contact karo."
        },
        {
            keywords: ["representative", "contact rep", "representative se baat"],
            answer: "Har ward ke representatives 'Representatives' page pe list hain unke phone/email ke saath. Representative apna alag login use karta hai apne ward ki complaints dekhne ke liye."
        },
        {
            keywords: ["image", "photo upload", "picture", "photo lagana"],
            answer: "Haan, complaint register karte waqt photo upload kar sakte ho (optional hai). Bas 'Choose File' pe click karke image select karo, submit se pehle preview bhi dikhega."
        },
        {
            keywords: ["status matlab", "pending matlab", "resolved matlab", "in progress matlab"],
            answer: "Status ka matlab: Pending = abhi dekha nahi gaya, In Progress = representative kaam kar raha hai, Resolved = solve ho gaya, Rejected = valid nahi mana gaya."
        },
        {
            keywords: ["contact", "support", "help", "madad"],
            answer: "Kisi bhi help ke liye 'About' page ke Contact section mein email/phone diya hua hai, ya representative se seedha contact kar sakte ho."
        },
        {
            keywords: ["hello", "hi", "hey", "namaste", "salam"],
            answer: "hello! Main CivicConnect ka helper bot hoon. Puchho: complaint kaise karein, status kaise check karein, ya ward ke baare mein."
        },
        {
            keywords: ["developer", "kisne banaya", "who made", "who developed", "banane wala", "creator"],
            answer: "CivicConnect ko Mirza Bismillah Baig ne banaya hai — BCA (Data Science) student, Nandigram Institute of Information Technology, Nanded. Ye unka final year project hai, jisme Flask, MySQL, HTML/CSS/JavaScript use hui hai."
        },
        {
            keywords: ["achha nagrik", "good citizen", "nagrik ki zimmedari", "civic duty", "responsibility of citizen", "citizen responsibility"],
            answer: "Ek achhe nagrik ki kuch zimmedariyan: apne aas-paas ki civic problems (garbage, road damage, etc.) samay pe report karna, public property ka dhyan rakhna, saaf-safai mein sahyog dena, aur apne ward representative se judkar samasyaon ko solve karwane mein madad karna. CivicConnect isi soch se bana hai — har nagrik ki awaaz seedha representative tak pahunchane ke liye."
        },
        {
            keywords: ["swachhata", "cleanliness", "safai", "environment", "paryavaran"],
            answer: "Swachhata aur environment ki dekhbhal har nagrik ki zimmedari hai — kachra sahi jagah dalna, paani/bijli waste na karna, aur apne mohalle ki civic problems CivicConnect jaise platform se report karna, ye sab milkar ek behtar shehar banate hain."
        },
        {
            keywords: ["voting", "vote", "matdan", "election"],
            answer: "Voting/matdan ek achhe nagrik ka bahut zaroori adhikar aur zimmedari hai — apne ward ke sahi representative ko chunna hi civic engagement ki shuruat hoti hai, jisse CivicConnect jaisi cheezein aur behtar kaam karti hain."
        },
        {
            keywords: ["thank you", "thanks", "shukriya", "dhanyawad", "thankyou"],
            answer: "Aapka swagat hai! 😊 Khushi hui madad kar ke. Kabhi bhi koi sawal ho, main yahin hoon. Civic issues report karte rehna, CivicConnect aapke saath hai!"
        }
    ];

    const fallback = "Maaf karna, mujhe iska jawab nahi pata. Kripya 'About' page se contact karo, ya dobara alag tarike se puchho (jaise: 'complaint kaise karein').";

    function getAnswer(question) {

        const q = question.toLowerCase();

        for (const item of faq) {
            for (const kw of item.keywords) {
                if (q.includes(kw)) {
                    return item.answer;
                }
            }
        }

        return fallback;
    }

    // ---------- Inject CSS ----------

    const style = document.createElement("style");
    style.innerHTML = `
        #cc-chat-toggle {
            position: fixed;
            bottom: 25px;
            right: 25px;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: linear-gradient(135deg, #0d6efd, #00c6ff);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 26px;
            cursor: pointer;
            box-shadow: 0 8px 20px rgba(13,110,253,.4);
            z-index: 9999;
            transition: .3s;
            font-family: sans-serif;
        }
        #cc-chat-toggle:hover {
            transform: scale(1.08);
        }
        #cc-chat-window {
            position: fixed;
            bottom: 95px;
            right: 25px;
            width: 320px;
            max-width: 90vw;
            height: 420px;
            max-height: 70vh;
            background: white;
            border-radius: 16px;
            box-shadow: 0 15px 40px rgba(0,0,0,.25);
            display: none;
            flex-direction: column;
            overflow: hidden;
            z-index: 9999;
            font-family: 'Poppins', sans-serif;
        }
        #cc-chat-header {
            background: linear-gradient(135deg, #0d6efd, #00c6ff);
            color: white;
            padding: 14px 18px;
            font-weight: 600;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        #cc-chat-header span.cc-close {
            cursor: pointer;
            font-size: 18px;
        }
        #cc-chat-body {
            flex: 1;
            padding: 12px;
            overflow-y: auto;
            background: #f4f7fb;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        .cc-msg {
            padding: 10px 14px;
            border-radius: 12px;
            max-width: 80%;
            font-size: 14px;
            line-height: 1.4;
        }
        .cc-msg.bot {
            background: #e5edff;
            color: #0d3b8c;
            align-self: flex-start;
            border-bottom-left-radius: 2px;
        }
        .cc-msg.user {
            background: #0d6efd;
            color: white;
            align-self: flex-end;
            border-bottom-right-radius: 2px;
        }
        #cc-chat-input-box {
            display: flex;
            border-top: 1px solid #eee;
            padding: 8px;
            gap: 8px;
        }
        #cc-chat-input {
            flex: 1;
            border: 1px solid #ddd;
            border-radius: 20px;
            padding: 8px 14px;
            outline: none;
            font-size: 14px;
        }
        #cc-chat-send {
            background: #0d6efd;
            color: white;
            border: none;
            border-radius: 50%;
            width: 38px;
            height: 38px;
            cursor: pointer;
            font-size: 16px;
        }
    `;
    document.head.appendChild(style);

    // ---------- Inject HTML ----------

    const toggle = document.createElement("div");
    toggle.id = "cc-chat-toggle";
    toggle.innerHTML = "💬";
    document.body.appendChild(toggle);

    const win = document.createElement("div");
    win.id = "cc-chat-window";
    win.innerHTML = `
        <div id="cc-chat-header">
            <span>CivicConnect Helper</span>
            <span class="cc-close">&times;</span>
        </div>
        <div id="cc-chat-body"></div>
        <div id="cc-chat-input-box">
            <input type="text" id="cc-chat-input" placeholder="Apna sawal likho...">
            <button id="cc-chat-send">➤</button>
        </div>
    `;
    document.body.appendChild(win);

    const body = win.querySelector("#cc-chat-body");
    const input = win.querySelector("#cc-chat-input");
    const sendBtn = win.querySelector("#cc-chat-send");
    const closeBtn = win.querySelector(".cc-close");

    function addMessage(text, sender) {
        const msg = document.createElement("div");
        msg.className = "cc-msg " + sender;
        msg.textContent = text;
        body.appendChild(msg);
        body.scrollTop = body.scrollHeight;
    }

    function handleSend() {
        const question = input.value.trim();
        if (!question) return;

        addMessage(question, "user");
        input.value = "";

        setTimeout(function () {
            addMessage(getAnswer(question), "bot");
        }, 400);
    }

    toggle.addEventListener("click", function () {
        const isOpen = win.style.display === "flex";
        win.style.display = isOpen ? "none" : "flex";

        if (!isOpen && body.children.length === 0) {
            addMessage("Namaste! Main CivicConnect Helper hoon. Puchho: complaint kaise karein, status kaise check karein, ward ke baare mein, developer kaun hai, ya ek achhe nagrik ki zimmedariyan.", "bot");
        }
    });

    closeBtn.addEventListener("click", function () {
        win.style.display = "none";
    });

    sendBtn.addEventListener("click", handleSend);

    input.addEventListener("keypress", function (e) {
        if (e.key === "Enter") {
            handleSend();
        }
    });

    } // end initChatbot

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initChatbot);
    } else {
        initChatbot();
    }

})();