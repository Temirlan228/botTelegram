from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Poll
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, PollAnswerHandler
import asyncio

TOKEN = '6859463150:AAHSU0HTSOZ5E1IWXh93ASZCQlwiSFbEQoI'  # Replace with your bot's token

questions = [
    {
        "category": "Geography",
        "question": "What is the capital of France?",
        "options": ["Paris", "London", "Berlin", "Madrid"],
        "correct_option_id": 0
    },
    {
        "category": "Geography",
        "question": "What is the capital of France?",
        "options": ["Paris", "London", "Berlin", "Madrid"],
        "correct_option_id": 0
    },
{
        "category": "Geography",
        "question": "What is the capital of France?",
        "options": ["Paris", "London", "Berlin", "Madrid"],
        "correct_option_id": 0
    },
    {
        "category": "Math",
        "question": "What is 2 + 2?",
        "options": ["3", "4", "5", "6"],
        "correct_option_id": 1
    },
    {
        "category": "Math",
        "question": "What is 2 + 2?",
        "options": ["3", "4", "5", "6"],
        "correct_option_id": 1
    },
    {
        "category": "Math",
        "question": "What is 2 + 2?",
        "options": ["3", "4", "5", "6"],
        "correct_option_id": 1
    },
    # Your questions with categories
]

# A dictionary to keep track of each user's state
user_states = {}

# Global dictionary to store scores
global_scores = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Geography", callback_data='Geography')],
        [InlineKeyboardButton("Math", callback_data='Math')],
        # Add more categories as needed
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Please choose a topic:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if query.data == 'review_answers':
        # Call the function to show answers
        await show_answers(update, context, user_id)
    else:
        user_states[user_id] = {"score": 0, "current_question_index": 0, "category": query.data, "answers": []}
        await send_next_question(context, user_id)

async def send_next_question(context: ContextTypes.DEFAULT_TYPE, user_id: int):
    user_state = user_states.get(user_id)
    if user_state is None:
        return

    category = user_state["category"]
    filtered_questions = [q for q in questions if q["category"] == category]

    if user_state["current_question_index"] >= len(filtered_questions):
        total_questions = len(filtered_questions)
        score = user_state["score"]
        keyboard = [[InlineKeyboardButton("Review Answers", callback_data='review_answers')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=user_id, text=f"You've completed all the {category} questions! Your result is {score}/{total_questions}.", reply_markup=reply_markup)
        return

    question = filtered_questions[user_state["current_question_index"]]
    await context.bot.send_poll(
        chat_id=user_id,
        question=question["question"],
        options=question["options"],
        type=Poll.QUIZ,
        correct_option_id=question["correct_option_id"],
        is_anonymous=False,
        explanation="Let's see if you got it right!"
    )

async def handle_quiz_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    answer = update.poll_answer
    user_id = answer.user.id
    user_state = user_states.get(user_id)

    if user_state is None:
        return

    category = user_state["category"]
    filtered_questions = [q for q in questions if q["category"] == category]
    question_index = user_state["current_question_index"]
    correct = answer.option_ids[0] == filtered_questions[question_index]["correct_option_id"]

    if correct:
        user_state["score"] += 1
        global_scores[user_id] = global_scores.get(user_id, 0) + 1
    user_state["answers"].append((filtered_questions[question_index]["question"], correct))

    user_state["current_question_index"] += 1
    await asyncio.sleep(1)
    await send_next_question(context, user_id)

async def show_answers(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    user_state = user_states.get(user_id)
    if user_state is None:
        return

    answers_text = "Your answers:\n"
    for idx, (question, correct) in enumerate(user_state["answers"], start=1):
        status = "Correct" if correct else "Incorrect"
        answers_text += f"{idx}. {question} - {status}\n"
    await context.bot.send_message(chat_id=user_id, text=answers_text)

async def show_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    leaderboard_text = "🏆 Leaderboard 🏆\n"
    sorted_scores = sorted(global_scores.items(), key=lambda item: item[1], reverse=True)
    for idx, (user_id, score) in enumerate(sorted_scores, start=1):
        user_info = await context.bot.get_chat(user_id)
        user_name = user_info.username or user_info.first_name  # Fallback to first_name
        leaderboard_text += f"{idx}. @{user_name}: {score} points\n"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=leaderboard_text)

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(PollAnswerHandler(handle_quiz_answer))
    application.add_handler(CommandHandler("leaderboard", show_leaderboard))

    application.run_polling()

if __name__ == '__main__':
    main()
