# Claude Prompts Integration Workflow Diagram

## Development Session Workflow

```mermaid
flowchart TD
    Start([Start Development Session]) --> ReadMemory[Read Memory Bank Files]
    ReadMemory --> CheckContext{Current Context Clear?}
    
    CheckContext -->|Yes| PlanWork[Plan Current Work]
    CheckContext -->|No| UpdateMemory[Update Memory Bank]
    UpdateMemory --> PlanWork
    
    PlanWork --> CheckExisting[Check for Existing Code]
    CheckExisting --> ExistingFound{Similar Code Found?}
    
    ExistingFound -->|Yes| ReuseCode[Reuse & Adapt Existing]
    ExistingFound -->|No| CreateNew[Create New Implementation]
    
    ReuseCode --> Implement[Implement Changes]
    CreateNew --> Implement
    
    Implement --> Test[Run VTuber Tests]
    Test --> TestPass{Tests Pass?}
    
    TestPass -->|No| Debug[Apply Circuit Breaker Debugging]
    TestPass -->|Yes| Document[Update Documentation]
    
    Debug --> DebugCount{Attempts < 3?}
    DebugCount -->|Yes| TryAgain[Try Different Approach]
    DebugCount -->|No| MultiModel[Use Multi-Model Analysis]
    
    TryAgain --> Implement
    MultiModel --> Gemini[Gemini: Architecture Analysis]
    Gemini --> GPT[GPT: Implementation Strategy]
    GPT --> Claude[Claude: Debug Analysis]
    Claude --> Implement
    
    Document --> UpdateMemoryFinal[Update Memory Bank]
    UpdateMemoryFinal --> Complete([Session Complete])
```

## VTuber-Specific Testing Workflow

```mermaid
flowchart TD
    CodeChange[Code Changes Made] --> TestType{What Changed?}
    
    TestType -->|Live2D| Live2DTest[Run Live2D Rendering Tests]
    TestType -->|Audio| AudioTest[Run Audio Pipeline Tests]
    TestType -->|AWS| AWSTest[Run AWS Integration Tests]
    TestType -->|Desktop| DesktopTest[Run Desktop Interaction Tests]
    TestType -->|Multiple| FullTest[Run Full VTuber Test Suite]
    
    Live2DTest --> PuppeteerLive2D[Puppeteer: Model Loading & Animation]
    AudioTest --> PuppeteerAudio[Puppeteer: STT/TTS Pipeline]
    AWSTest --> PuppeteerAWS[Puppeteer: Claude Integration]
    DesktopTest --> PuppeteerDesktop[Puppeteer: Drag & System Tray]
    FullTest --> PuppeteerFull[Puppeteer: Complete User Flow]
    
    PuppeteerLive2D --> ValidateResults[Validate Test Results]
    PuppeteerAudio --> ValidateResults
    PuppeteerAWS --> ValidateResults
    PuppeteerDesktop --> ValidateResults
    PuppeteerFull --> ValidateResults
    
    ValidateResults --> TestSuccess{All Tests Pass?}
    TestSuccess -->|Yes| UpdateMemory[Update Memory Bank with Results]
    TestSuccess -->|No| CircuitBreaker[Apply Circuit Breaker Debugging]
    
    CircuitBreaker --> DebugSession[Document Debugging Session]
    DebugSession --> FixIssue[Apply Systematic Fix]
    FixIssue --> CodeChange
    
    UpdateMemory --> Complete[Testing Complete]
```

## Multi-Model AI Integration Workflow

```mermaid
flowchart TD
    Task[Development Task] --> TaskType{Task Type?}
    
    TaskType -->|Architecture Design| UseGemini[Use Gemini 2.5-Pro]
    TaskType -->|Code Implementation| UseGPT[Use GPT-5]
    TaskType -->|Analysis & Debugging| UseClaude[Use Claude]
    TaskType -->|Complex Integration| UseMultiple[Use Multi-Model Sequence]
    
    UseGemini --> GeminiTasks[System Design<br/>User Experience<br/>Component Architecture]
    UseGPT --> GPTTasks[Algorithm Implementation<br/>Performance Optimization<br/>Feature Coding]
    UseClaude --> ClaudeTasks[Code Analysis<br/>Bug Investigation<br/>Context Understanding]
    
    UseMultiple --> Sequence[Sequential Model Usage]
    Sequence --> Step1[1. Claude: Analyze Current State]
    Step1 --> Step2[2. Gemini: Design Solution]
    Step2 --> Step3[3. GPT: Implement Code]
    Step3 --> Step4[4. Claude: Verify & Test]
    
    GeminiTasks --> DocumentDecision[Document AI Model Decision]
    GPTTasks --> DocumentDecision
    ClaudeTasks --> DocumentDecision
    Step4 --> DocumentDecision
    
    DocumentDecision --> UpdateMemoryBank[Update Memory Bank with AI Insights]
    UpdateMemoryBank --> Complete[Task Complete]
```

## Memory Bank Update Workflow

```mermaid
flowchart TD
    Trigger[Memory Bank Update Trigger] --> TriggerType{Update Type?}
    
    TriggerType -->|Session Start| ReadAll[Read ALL Memory Bank Files]
    TriggerType -->|Feature Complete| UpdateFeature[Update Feature Documentation]
    TriggerType -->|Bug Fixed| UpdateDebugging[Update Debugging Sessions]
    TriggerType -->|Manual Request| ReviewAll[Review ALL Files for Updates]
    
    ReadAll --> SessionContext[Establish Session Context]
    UpdateFeature --> FeatureFiles[Update Feature-Specific Files]
    UpdateDebugging --> DebugFiles[Update Debugging Documentation]
    ReviewAll --> ComprehensiveReview[Comprehensive Memory Review]
    
    SessionContext --> ActiveContext[Update activeContext.md]
    FeatureFiles --> ProgressUpdate[Update progress.md]
    DebugFiles --> PatternsUpdate[Update systemPatterns.md]
    ComprehensiveReview --> AllFiles[Update All Relevant Files]
    
    ActiveContext --> Validate[Validate Memory Bank Consistency]
    ProgressUpdate --> Validate
    PatternsUpdate --> Validate
    AllFiles --> Validate
    
    Validate --> MemoryComplete[Memory Bank Updated]
```

## Circuit Breaker Debugging Workflow

```mermaid
flowchart TD
    Error[Error Encountered] --> ReadError[Read COMPLETE Error Message]
    ReadError --> ErrorType{VTuber Error Type?}
    
    ErrorType -->|Live2D Model Loading| Live2DDebug[Live2D Debugging Pattern]
    ErrorType -->|Audio Sync Issues| AudioDebug[Audio Pipeline Debugging]
    ErrorType -->|AWS Connection| AWSDebug[AWS Integration Debugging]
    ErrorType -->|WebSocket Issues| WSDebug[WebSocket Debugging]
    ErrorType -->|Unknown| GenericDebug[Generic Debugging Pattern]
    
    Live2DDebug --> Hypothesis1[Form Specific Hypothesis]
    AudioDebug --> Hypothesis1
    AWSDebug --> Hypothesis1
    WSDebug --> Hypothesis1
    GenericDebug --> Hypothesis1
    
    Hypothesis1 --> MinimalTest[Make MINIMAL Change to Test]
    MinimalTest --> TestResult[Observe Result]
    TestResult --> HypothesisCorrect{Hypothesis Confirmed?}
    
    HypothesisCorrect -->|Yes| ApplyFix[Apply Proper Fix]
    HypothesisCorrect -->|No| CountAttempts[Count Debugging Attempts]
    
    CountAttempts --> AttemptCount{Attempts < 3?}
    AttemptCount -->|Yes| NewHypothesis[Try Different Approach]
    AttemptCount -->|No| CircuitBreaker[CIRCUIT BREAKER ACTIVATED]
    
    NewHypothesis --> Hypothesis1
    CircuitBreaker --> StepBack[Step Back & Reassess]
    StepBack --> MultiModelHelp[Use Different AI Model]
    MultiModelHelp --> FreshPerspective[Get Fresh Perspective]
    FreshPerspective --> Hypothesis1
    
    ApplyFix --> DocumentSolution[Document Solution in Memory Bank]
    DocumentSolution --> Complete[Debugging Complete]
```

## Integration Points with Existing Project

```mermaid
flowchart LR
    subgraph "Existing Project"
        ExistingTodo[implementation-todo-list.md]
        AWSPlan[aws-migration-plan.md]
        StatusReport[FINAL_STATUS_REPORT.md]
        WorkingSystem[Working VTuber System]
    end
    
    subgraph "Claude Prompts Integration"
        MemoryBank[Memory Bank System]
        CircuitBreaker[Circuit Breaker Debugging]
        PuppeteerTests[Puppeteer VTuber Testing]
        MultiModel[Multi-Model AI Workflows]
    end
    
    subgraph "Enhanced Development"
        SystematicDebugging[Systematic Debugging]
        ContextContinuity[Context Continuity]
        AutomatedTesting[Automated Testing]
        OptimizedAI[Optimized AI Usage]
    end
    
    ExistingTodo --> MemoryBank
    AWSPlan --> CircuitBreaker
    StatusReport --> PuppeteerTests
    WorkingSystem --> MultiModel
    
    MemoryBank --> ContextContinuity
    CircuitBreaker --> SystematicDebugging
    PuppeteerTests --> AutomatedTesting
    MultiModel --> OptimizedAI
    
    ContextContinuity --> ImprovedDev[Improved Development Efficiency]
    SystematicDebugging --> ImprovedDev
    AutomatedTesting --> ImprovedDev
    OptimizedAI --> ImprovedDev
```

## Implementation Timeline

```mermaid
gantt
    title Claude Prompts Integration Timeline
    dateFormat  YYYY-MM-DD
    section Week 1: Foundation
    Memory Bank Setup           :active, w1-memory, 2024-01-15, 2d
    Circuit Breaker Basics      :w1-circuit, after w1-memory, 2d
    Basic Puppeteer Tests       :w1-puppet, after w1-circuit, 2d
    Multi-Model Foundation      :w1-multi, after w1-puppet, 1d
    
    section Week 2: Enhancement
    VTuber Debugging Patterns   :w2-debug, 2024-01-22, 3d
    Advanced Puppeteer Tests    :w2-puppet, after w2-debug, 3d
    Testing Integration         :w2-integration, after w2-puppet, 1d
    
    section Week 3: Quality
    Code Reuse Analysis         :w3-reuse, 2024-01-29, 3d
    File Organization           :w3-org, after w3-reuse, 2d
    Quality Metrics             :w3-quality, after w3-org, 2d
    
    section Week 4: Integration
    Full Multi-Model Workflow   :w4-multi, 2024-02-05, 3d
    Complete Testing Suite      :w4-testing, after w4-multi, 2d
    Final Integration           :w4-final, after w4-testing, 2d
```

## Success Metrics Dashboard

```mermaid
flowchart TD
    Metrics[Success Metrics] --> Technical[Technical Metrics]
    Metrics --> Quality[Quality Metrics]
    Metrics --> Process[Process Metrics]
    
    Technical --> MemoryUsage[Memory Bank Usage: 100%]
    Technical --> DebugEfficiency[Debug Efficiency: +50%]
    Technical --> CodeReuse[Code Reuse Rate: 80%]
    Technical --> TestCoverage[Test Coverage: 90%+]
    
    Quality --> BugReduction[Bug Reduction: 70%]
    Quality --> DevSpeed[Development Speed: +40%]
    Quality --> Documentation[Documentation Quality: Complete]
    Quality --> MultiModelSuccess[Multi-Model Integration: Success]
    
    Process --> SessionStart[Sessions Start with Memory: 100%]
    Process --> CircuitBreakerUse[Circuit Breaker Usage: Active]
    Process --> AutomatedTesting[Automated Testing: Operational]
    Process --> AIOptimization[AI Model Optimization: Implemented]
```

This workflow diagram shows how the Claude Prompts best practices integrate seamlessly with your existing AWS VTuber LLM development process, enhancing rather than replacing your current excellent work.