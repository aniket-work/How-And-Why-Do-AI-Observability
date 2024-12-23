-- Event Types Distribution
WITH event_types AS (
  SELECT
    JSON_EXTRACT(raw_response, '$.choices[0].message.content')::json->>'event_type' as event_type,
    COUNT(*) as count
  FROM openai_records_*
  GROUP BY 1
)
SELECT json_group_array(
  json_object(
    'name', event_type,
    'value', count
  )
) as eventTypes,

-- Risk Levels Trend
(
  SELECT json_group_array(
    json_group_object(
      'timestamp', strftime(timestamp, '%Y-%m-%d %H:%M'),
      'high', SUM(CASE WHEN risk_level = 'high' THEN 1 ELSE 0 END),
      'medium', SUM(CASE WHEN risk_level = 'medium' THEN 1 ELSE 0 END),
      'low', SUM(CASE WHEN risk_level = 'low' THEN 1 ELSE 0 END)
    )
  )
  FROM (
    SELECT
      timestamp,
      JSON_EXTRACT(raw_response, '$.choices[0].message.content')::json->>'risk_level' as risk_level
    FROM openai_records_*
    GROUP BY date_trunc('minute', timestamp)
  )
) as riskTrend,

-- Protocol Distribution
(
  SELECT json_group_array(
    json_object(
      'name', protocol,
      'count', count
    )
  )
  FROM (
    SELECT
      JSON_EXTRACT(raw_response, '$.choices[0].message.content')::json->>'protocol' as protocol,
      COUNT(*) as count
    FROM openai_records_*
    GROUP BY 1
  )
) as protocols,

-- Event Frequency
(
  SELECT json_group_array(
    json_object(
      'timestamp', strftime(timestamp, '%Y-%m-%d %H:%M'),
      'events', count
    )
  )
  FROM (
    SELECT
      date_trunc('minute', timestamp) as timestamp,
      COUNT(*) as count
    FROM openai_records_*
    GROUP BY 1
    ORDER BY 1
  )
) as frequency;