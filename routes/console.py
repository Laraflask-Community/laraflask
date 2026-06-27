"""
Console Routes — Laraflask
Define scheduled tasks here.

Run: python artisan.py schedule:run
Daemon: python artisan.py schedule:work
"""

# Schedule is injected automatically by the framework

# ─── Example Scheduled Tasks ──────────────────────────────────────────────────

# Schedule.command('cache:clear').daily()
# Schedule.command('db:seed').weekly()

# Schedule.call(lambda: print('Heartbeat!')).every_minute()

# Schedule.job('App\\Jobs\\GenerateReportJob').daily_at('02:00')

# Schedule.command('backup:run').daily_at('01:00').environments('production')

# Schedule.command('queue:work', ['--stop-when-empty']).every_minute()
