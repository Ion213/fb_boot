from fbchat_muqit import Message, ThreadType

async def remove_user(self, author_id, user_message, thread_id, thread_type):
    """Handles removing a user from the group, only allowing admins to do so."""

    # Ensure command is used in a group
    if thread_type != ThreadType.GROUP:
        alert = "⚠️ This command can only be used in group chats!"
        await self.send(Message(text=alert), thread_id=thread_id, thread_type=thread_type)
        return

    # Fetch group info
    group_info = await self.fetchThreadInfo(thread_id)
    group_info = group_info[thread_id]

    # Get admin list
    admins = group_info.admins if group_info.admins else []

    # Check if author is an admin
    if author_id not in admins:
        alert = "⚠️ Only group admins can remove users from the group!"
        await self.send(Message(text=alert), thread_id=thread_id, thread_type=thread_type)
        return

    parts = user_message.split(" ")

    if len(parts) > 1:  # Ensure there's something after /remove
        user_id = parts[1].strip()  # Extract the user ID after /remove
        if user_id:
            try:
                # Attempt to remove the user from the group
                await self.removeUserFromGroup(user_id, thread_id)
                alert = f"✅ User {user_id} has been removed from the group by an admin!"
                print(alert)
                await self.send(Message(text=alert), thread_id=thread_id, thread_type=thread_type)
            except Exception as e:
                error_message = f"⚠️ Failed to remove user {user_id}. Error: {e}"
                print(error_message)
                await self.send(Message(text=error_message), thread_id=thread_id, thread_type=thread_type)
        else:
            alert = "⚠️ Please provide a valid user ID to remove!"
            await self.send(Message(text=alert), thread_id=thread_id, thread_type=thread_type)
    else:
        alert = "⚠️ Please provide a user ID after /remove! Example: /remove user_id"
        await self.send(Message(text=alert), thread_id=thread_id, thread_type=thread_type)
