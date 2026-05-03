# AI Tools & Prompts Used

## Tool Used
Claude AI (claude.ai)

## My Approach

I used Claude AI as a learning assistant — not to generate 
code blindly. My approach was:

1. I read the assignment carefully first
2. I decided the tech stack based on my SRE experience
3. I asked Claude to explain concepts I needed to understand
4. I made all architectural decisions myself
5. I debugged issues by understanding the errors first

## Topics I Asked Claude to Explain

- How debouncing works at scale
- Difference between Redis Streams and Kafka
- How async/await improves throughput in Python
- PostgreSQL vs MongoDB for different data types
- How Prometheus scrapes metrics from FastAPI

## Decisions I Made Myself

- Chose FastAPI because I knew Python and needed async
- Chose Redis Streams over Kafka — I was honest that
  I don't have deep Kafka experience yet
- Chose PostgreSQL for Work Items because I have used
  it in my previous projects (URL Shortener, CloudOptima)
- Designed the debounce window at 10 seconds based on
  the assignment requirement
- Chose Prometheus + Grafana because I already used it
  in my URL Shortener project

## What This Shows

I know how to use AI as a tool — not as a replacement
for thinking. Every line of code in this project I can
read and explain.
