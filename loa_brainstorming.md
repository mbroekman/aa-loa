# Brainstorming aa-loa

## Data Models
1. `LeaveOfAbsence`
   - `user`: ForeignKey(User)
   - `start_date`: DateField
   - `end_date`: DateField
   - `reason`: TextField
   - `submitted_by`: ForeignKey(User) (For proxy)
   - `cancelled`: BooleanField (For early cancel)
   - `notified_return`: BooleanField (To track if we sent the welcome back DM)

## Integrations
- Discord Role: Create a setting for a Django Group `On Leave`. When LOA becomes active, add user to this group. When it expires, remove them. Alliance Auth will automatically sync this to Discord and TS.
- Discord Webhook: Send message to a configured webhook when LOA is created/updated.
- Discord DM: Use `aa-discordbot` or standard Auth notifications to send the Welcome Back message.
- Activity Trackers: Expose an API or provide a Django Signal (`loa_started`, `loa_ended`) that other modules (like Opcalendar) can listen to. Or just rely on the `On Leave` group for exemptions!

## Views
- `loa_index`: User's own LOAs, form to create new.
- `loa_director`: Restricted to HR. List of all LOAs, proxy submit form.

