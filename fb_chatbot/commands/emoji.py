from fbchat_muqit import Message, ThreadType

async def change_emoji(self, author_id, user_message, thread_id, thread_type):
    """Handles changing the group emoji if the user is an admin."""
    
    if thread_type == ThreadType.GROUP:
        group_info = await self.fetchThreadInfo(thread_id)
        group_info = group_info[thread_id]

        # Check if the group has admins
        admins = group_info.admins if group_info.admins else []

        if author_id in admins:  # Only allow group admins to change emoji
            new_emoji = user_message.split("/emoji", 1)[1].strip()
            if new_emoji:
                await self.changeThreadEmoji(new_emoji, thread_id)
                print(f"✅ Group emoji changed to {new_emoji}, BY USER ID: {author_id}")
                await self.send(Message(text=f"✅ Group emoji changed to {new_emoji}, BY USER ID:{author_id}"), thread_id=thread_id, thread_type=thread_type)
            else:
                await self.send(Message(text="⚠ Please provide an emoji! Example: /emoji 😊"), thread_id=thread_id, thread_type=thread_type)
        else:
            await self.send(Message(text="⚠ Only group admins can change the emoji!"), thread_id=thread_id, thread_type=thread_type)
