"""
Console Routes - Laraflask
==========================

Define scheduled tasks (cron jobs) here. The framework's scheduler evaluates
this file and executes matching tasks at the appropriate intervals.

`Schedule` is injected automatically by the framework at runtime.
Do NOT import it -- use it directly as a module-level global.

Running the scheduler:
    Single pass:  python artisan.py schedule:run
    Daemon mode:  python artisan.py schedule:work

Available scheduling frequencies:
    .every_minute()           - Run every minute
    .every_five_minutes()     - Run every 5 minutes
    .every_fifteen_minutes()  - Run every 15 minutes
    .every_thirty_minutes()   - Run every 30 minutes
    .hourly()                 - Run once per hour
    .hourly_at(17)            - Run at :17 past every hour
    .daily()                  - Run once daily at midnight
    .daily_at('13:00')        - Run daily at 1:00 PM
    .weekly()                 - Run once per week (Sunday midnight)
    .weekly_on(1, '08:00')    - Run weekly on Monday at 8:00 AM
    .monthly()                - Run once per month (1st at midnight)
    .quarterly()              - Run once per quarter
    .yearly()                 - Run once per year

Chaining options:
    .environments('production')       - Only run in production
    .without_overlapping()            - Prevent overlapping runs
    .run_in_background()              - Run task in background
    .even_in_maintenance_mode()       - Run even during maintenance
    .on_one_server()                  - Run on single server only
"""


# =============================================================================
# High-Frequency Tasks (every minute to every 15 minutes)
# =============================================================================
# Tasks that need to run very frequently for near-real-time processing.

# Schedule.call(lambda: print('Heartbeat!')).every_minute()
# Schedule.command('queue:work', ['--stop-when-empty']).every_minute()
# Schedule.command('queue:retry', ['all']).every_five_minutes()


# =============================================================================
# Hourly Tasks
# =============================================================================
# Tasks that aggregate data or perform periodic checks.

# Schedule.command('cache:prune-stale').hourly()
# Schedule.job('App\\Jobs\\SyncExternalDataJob').hourly_at(30)


# =============================================================================
# Daily Tasks
# =============================================================================
# Maintenance, cleanup, and reporting tasks that run once per day.

# Schedule.command('cache:clear').daily()
# Schedule.command('backup:run').daily_at('01:00').environments('production')
# Schedule.job('App\\Jobs\\GenerateReportJob').daily_at('02:00')
# Schedule.command('log:clear').daily_at('03:00')
# Schedule.command('telescope:prune').daily_at('04:00')


# =============================================================================
# Weekly Tasks
# =============================================================================
# Less frequent maintenance and bulk operations.

# Schedule.command('db:seed').weekly()
# Schedule.job('App\\Jobs\\WeeklyDigestJob').weekly_on(1, '09:00')


# =============================================================================
# Monthly / Quarterly / Yearly Tasks
# =============================================================================
# Long-interval tasks for archiving and compliance.

# Schedule.job('App\\Jobs\\ArchiveOldRecordsJob').monthly()
# Schedule.job('App\\Jobs\\ComplianceReportJob').quarterly()
# Schedule.job('App\\Jobs\\AnnualAuditJob').yearly()
