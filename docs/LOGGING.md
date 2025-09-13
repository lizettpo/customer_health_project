# Logging Configuration

The Customer Health Score API includes comprehensive logging for monitoring, debugging, and auditing purposes.

## Log Configuration

### Log Format
All logs use the following format:
```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

Example:
```
2024-01-15 10:30:45,123 - __main__ - INFO - 🚀 Starting Customer Health Score API...
2024-01-15 10:30:45,124 - __main__ - INFO - Fetching customers with health_status filter: healthy
2024-01-15 10:30:45,125 - __main__ - INFO - Successfully fetched 25 customers
```

### Log Levels
- **INFO**: Normal operations, startup/shutdown, successful operations
- **WARNING**: Invalid requests, missing customers, recoverable issues
- **ERROR**: Exceptions, failed operations, system errors

### Log Rotation
- **File Size Limit**: 10MB per log file
- **Backup Count**: 5 files (app.log, app.log.1, app.log.2, etc.)
- **Total Storage**: ~50MB maximum for logs

## Log Outputs

### Console Output
All logs are displayed in the console/terminal when running the application. This includes:
- Docker container logs (`docker-compose logs -f`)
- Local development (`python -m uvicorn main:app --reload`)

### File Output
Logs are written to files in the `backend/logs/` directory:
- **Primary Log**: `backend/logs/app.log`
- **Rotated Logs**: `app.log.1`, `app.log.2`, etc.

### Docker Volume Persistence
When running in Docker, logs are persisted using the `backend_logs` volume:
```yaml
volumes:
  - backend_logs:/app/logs  # Persistent log storage
```

## Log Contents

### Startup/Shutdown Events
```
🚀 Starting Customer Health Score API...
Environment: production
Database URL: sqlite:///./data/customer_health.db
✅ Database tables created/verified
📊 Database empty - populating with sample data...
✅ Sample data populated successfully!
🎉 API startup completed successfully!
```

### API Request Logging
```
INFO - Fetching customers with health_status filter: at_risk
INFO - Successfully fetched 12 customers
INFO - Fetching health detail for customer 5
INFO - Successfully calculated health score for customer 5: 67.5
INFO - Recording payment event for customer 3
INFO - Successfully recorded payment event for customer 3
```

### Error Logging
```
WARNING - Customer 999 not found
WARNING - Invalid event data for customer 5: Missing required field 'amount'
ERROR - Error fetching customers: Database connection failed
ERROR - Error recording event for customer 5: ValidationError - Invalid event type
```

## Accessing Logs

### During Development
```bash
# View logs in real-time
docker-compose logs -f backend

# View only recent logs
docker-compose logs --tail=100 backend

# View logs from specific service
docker-compose -f docker-compose.dev-all.yml logs -f backend
```

### Log File Access
```bash
# Access log files directly (if running locally)
tail -f backend/logs/app.log

# Access via Docker volume
docker run --rm -v customer_health_project_backend_logs:/logs alpine ls -la /logs/
docker run --rm -v customer_health_project_backend_logs:/logs alpine cat /logs/app.log
```

### Production Log Management
```bash
# Copy logs from Docker volume to host
docker run --rm -v customer_health_project_backend_logs:/logs -v $(pwd):/backup alpine cp -r /logs/ /backup/

# View current log file size
docker run --rm -v customer_health_project_backend_logs:/logs alpine du -h /logs/

# Clear old logs (if needed)
docker run --rm -v customer_health_project_backend_logs:/logs alpine sh -c "rm /logs/app.log.*"
```

## Log Monitoring

### Key Metrics to Monitor
- **Error Rate**: Count of ERROR level logs
- **Response Times**: Time between request and success logs
- **Customer Activity**: Event recording frequency
- **Health Score Calculations**: Frequency and success rate
- **Database Operations**: Connection issues, query failures

### Log Analysis Examples
```bash
# Count errors in last 1000 lines
docker-compose logs --tail=1000 backend | grep "ERROR" | wc -l

# Find customer-specific issues
docker-compose logs backend | grep "customer 123"

# Monitor event recording
docker-compose logs backend | grep "Recording.*event"

# Check health score calculations
docker-compose logs backend | grep "health score"
```

## Log Security

### Sensitive Information
The logging system is configured to avoid logging:
- Customer personal data (emails, names are only logged with IDs)
- API keys or authentication tokens
- Detailed event_data contents (only event types are logged)
- Database connection strings with passwords

### Log Access Control
- Log files are created with restricted permissions
- Docker volumes provide isolation
- Production deployments should implement log forwarding to secure systems

## Integration with Monitoring Systems

### Log Forwarding
For production deployments, consider forwarding logs to:
- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Fluentd** + centralized storage
- **Cloud Logging** (AWS CloudWatch, GCP Logging, Azure Monitor)

### Example Docker Compose Log Driver
```yaml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    # or for centralized logging:
    logging:
      driver: "fluentd"
      options:
        fluentd-address: "localhost:24224"
        tag: "customer-health-api"
```

## Troubleshooting

### Common Log Issues
1. **Logs not appearing**: Check volume mounts and permissions
2. **Log files too large**: Verify rotation is working, check disk space
3. **Missing startup logs**: Check for configuration errors, database issues
4. **Permission denied**: Ensure proper Docker volume permissions

### Debug Logging
To enable debug logging, modify `main.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```

Or set environment variable:
```bash
export LOG_LEVEL=DEBUG
docker-compose up -d
```

## Best Practices

1. **Monitor Disk Space**: Regularly check log volume usage
2. **Archive Old Logs**: Implement log archival for long-term storage
3. **Alert on Errors**: Set up monitoring alerts for error patterns
4. **Regular Log Review**: Periodically review logs for performance issues
5. **Structured Logging**: Consider JSON formatting for better parsing
6. **Log Correlation**: Use request IDs for tracking requests across services