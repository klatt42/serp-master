"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Loader2, FileText, Calendar, Download, Plus, X } from "lucide-react";

interface TemplateRequest {
  platform: string;
  keyword: string;
  intent: string;
  content_type?: string;
}

interface ContentTemplate {
  platform: string;
  structure: any;
  metadata: {
    keyword: string;
    intent: string;
    platform: string;
    content_type: string;
    estimated_creation_time: string;
  };
  [key: string]: any;
}

interface CalendarRequest {
  content_items: Array<{
    platform: string;
    keyword: string;
    title?: string;
  }>;
  start_date: string;
  duration_weeks: number;
  frequency: string;
}

interface CalendarItem {
  platform: string;
  keyword: string;
  scheduled_date: string;
  week_number: number;
  time_slot_reason: string;
  title?: string;
}

interface ContentCalendar {
  start_date: string;
  end_date: string;
  duration_weeks: number;
  frequency: string;
  scheduled_content: CalendarItem[];
  summary: {
    total_items: number;
    by_platform: { [key: string]: number };
    by_week: { [key: string]: any };
  };
}

export default function ContentStudioPage() {
  const [activeTab, setActiveTab] = useState("templates");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Template Generator State
  const [templatePlatform, setTemplatePlatform] = useState("youtube");
  const [templateKeyword, setTemplateKeyword] = useState("");
  const [templateIntent, setTemplateIntent] = useState("research");
  const [generatedTemplate, setGeneratedTemplate] = useState<ContentTemplate | null>(null);

  // Calendar Builder State
  const [calendarItems, setCalendarItems] = useState<Array<{ platform: string; keyword: string; title: string }>>([]);
  const [newItemPlatform, setNewItemPlatform] = useState("youtube");
  const [newItemKeyword, setNewItemKeyword] = useState("");
  const [newItemTitle, setNewItemTitle] = useState("");
  const [startDate, setStartDate] = useState("");
  const [durationWeeks, setDurationWeeks] = useState(12);
  const [frequency, setFrequency] = useState("weekly");
  const [generatedCalendar, setGeneratedCalendar] = useState<ContentCalendar | null>(null);

  const platforms = [
    { id: "youtube", name: "YouTube" },
    { id: "tiktok", name: "TikTok" },
    { id: "blog", name: "Blog" },
    { id: "instagram", name: "Instagram" },
    { id: "reddit", name: "Reddit" },
  ];

  const intents = [
    { id: "research", name: "Research" },
    { id: "purchase", name: "Purchase" },
    { id: "entertainment", name: "Entertainment" },
    { id: "education", name: "Education" },
  ];

  const frequencies = [
    { id: "daily", name: "Daily" },
    { id: "twice_weekly", name: "Twice Weekly" },
    { id: "weekly", name: "Weekly" },
    { id: "biweekly", name: "Bi-Weekly" },
    { id: "monthly", name: "Monthly" },
  ];

  // Template Generation
  const generateTemplate = async () => {
    if (!templateKeyword.trim()) {
      setError("Please enter a keyword");
      return;
    }

    setLoading(true);
    setError(null);
    setGeneratedTemplate(null);

    try {
      const requestData: TemplateRequest = {
        platform: templatePlatform,
        keyword: templateKeyword.trim(),
        intent: templateIntent,
      };

      const response = await fetch("http://localhost:8000/api/content/template", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestData),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      setGeneratedTemplate(data.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Template generation failed");
      console.error("Template generation error:", err);
    } finally {
      setLoading(false);
    }
  };

  // Calendar Management
  const addCalendarItem = () => {
    if (!newItemKeyword.trim()) {
      return;
    }

    setCalendarItems([
      ...calendarItems,
      {
        platform: newItemPlatform,
        keyword: newItemKeyword.trim(),
        title: newItemTitle.trim() || newItemKeyword.trim(),
      },
    ]);

    setNewItemKeyword("");
    setNewItemTitle("");
  };

  const removeCalendarItem = (index: number) => {
    setCalendarItems(calendarItems.filter((_, i) => i !== index));
  };

  const generateCalendar = async () => {
    if (calendarItems.length === 0) {
      setError("Please add at least one content item");
      return;
    }

    if (!startDate) {
      setError("Please select a start date");
      return;
    }

    setLoading(true);
    setError(null);
    setGeneratedCalendar(null);

    try {
      const requestData: CalendarRequest = {
        content_items: calendarItems,
        start_date: startDate,
        duration_weeks: durationWeeks,
        frequency: frequency,
      };

      const response = await fetch("http://localhost:8000/api/content/calendar", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestData),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      setGeneratedCalendar(data.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Calendar generation failed");
      console.error("Calendar generation error:", err);
    } finally {
      setLoading(false);
    }
  };

  const exportCalendar = async () => {
    if (!generatedCalendar) return;

    try {
      const response = await fetch("http://localhost:8000/api/content/calendar/export", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(generatedCalendar),
      });

      if (!response.ok) {
        throw new Error(`Export error: ${response.status}`);
      }

      const data = await response.json();

      // Create CSV content
      const csvHeaders = ["Subject", "Start Date", "Start Time", "End Date", "End Time", "Description", "Location"];
      const csvRows = data.data.items.map((item: any) =>
        [
          item.Subject,
          item["Start Date"],
          item["Start Time"],
          item["End Date"],
          item["End Time"],
          item.Description.replace(/\n/g, " "),
          item.Location,
        ].map(val => `"${val}"`).join(",")
      );

      const csvContent = [csvHeaders.join(","), ...csvRows].join("\n");

      // Download CSV
      const blob = new Blob([csvContent], { type: "text/csv" });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "content-calendar.csv";
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Export failed");
      console.error("Calendar export error:", err);
    }
  };

  const formatDate = (isoString: string) => {
    const date = new Date(isoString);
    return date.toLocaleDateString("en-US", {
      weekday: "short",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Content Studio</h1>
        <p className="text-gray-600">
          Generate platform-specific templates and build automated content calendars
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-2 mb-8">
          <TabsTrigger value="templates">
            <FileText className="mr-2 h-4 w-4" />
            Template Generator
          </TabsTrigger>
          <TabsTrigger value="calendar">
            <Calendar className="mr-2 h-4 w-4" />
            Calendar Builder
          </TabsTrigger>
        </TabsList>

        {/* Template Generator Tab */}
        <TabsContent value="templates">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Input Section */}
            <Card>
              <CardHeader>
                <CardTitle>Generate Content Template</CardTitle>
                <CardDescription>
                  Create platform-optimized content frameworks
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="template-platform">Platform</Label>
                  <Select value={templatePlatform} onValueChange={setTemplatePlatform}>
                    <SelectTrigger id="template-platform">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {platforms.map((platform) => (
                        <SelectItem key={platform.id} value={platform.id}>
                          {platform.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="template-keyword">Keyword/Topic *</Label>
                  <Input
                    id="template-keyword"
                    placeholder="e.g., best running shoes"
                    value={templateKeyword}
                    onChange={(e) => setTemplateKeyword(e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="template-intent">Content Intent</Label>
                  <Select value={templateIntent} onValueChange={setTemplateIntent}>
                    <SelectTrigger id="template-intent">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {intents.map((intent) => (
                        <SelectItem key={intent.id} value={intent.id}>
                          {intent.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {error && activeTab === "templates" && (
                  <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                    {error}
                  </div>
                )}

                <Button onClick={generateTemplate} disabled={loading} className="w-full">
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <FileText className="mr-2 h-4 w-4" />
                      Generate Template
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>

            {/* Template Display */}
            <Card>
              <CardHeader>
                <CardTitle>Generated Template</CardTitle>
                <CardDescription>
                  {generatedTemplate
                    ? `Ready-to-use ${generatedTemplate.platform} template`
                    : "Template will appear here"}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {generatedTemplate ? (
                  <div className="space-y-4">
                    {/* Metadata */}
                    <div className="bg-blue-50 border border-blue-200 rounded p-4">
                      <h4 className="font-semibold mb-2">Template Info</h4>
                      <div className="space-y-1 text-sm">
                        <p>
                          <span className="text-gray-600">Platform:</span>{" "}
                          <Badge className="ml-2 capitalize">{generatedTemplate.metadata.platform}</Badge>
                        </p>
                        <p>
                          <span className="text-gray-600">Keyword:</span>{" "}
                          <span className="font-medium">{generatedTemplate.metadata.keyword}</span>
                        </p>
                        <p>
                          <span className="text-gray-600">Estimated Time:</span>{" "}
                          <span className="font-medium">
                            {generatedTemplate.metadata.estimated_creation_time}
                          </span>
                        </p>
                      </div>
                    </div>

                    {/* Structure */}
                    <div>
                      <h4 className="font-semibold mb-2">Content Structure</h4>
                      <div className="bg-gray-50 border border-gray-200 rounded p-4">
                        <pre className="text-xs overflow-auto max-h-96">
                          {JSON.stringify(generatedTemplate.structure, null, 2)}
                        </pre>
                      </div>
                    </div>

                    {/* Title/Hook Suggestions */}
                    {(generatedTemplate.title_suggestions ||
                      generatedTemplate.hook_variations ||
                      generatedTemplate.headline_formulas ||
                      generatedTemplate.caption_formulas) && (
                      <div>
                        <h4 className="font-semibold mb-2">Suggestions</h4>
                        <div className="space-y-2">
                          {(
                            generatedTemplate.title_suggestions ||
                            generatedTemplate.hook_variations ||
                            generatedTemplate.headline_formulas ||
                            generatedTemplate.caption_formulas ||
                            []
                          ).map((suggestion: string, index: number) => (
                            <div
                              key={index}
                              className="bg-white border border-gray-200 rounded p-3 text-sm"
                            >
                              {suggestion}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-12 text-gray-400">
                    <FileText className="mx-auto h-12 w-12 mb-2" />
                    <p>Generate a template to see results</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Calendar Builder Tab */}
        <TabsContent value="calendar">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Input Section */}
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Add Content Items</CardTitle>
                  <CardDescription>Build your content plan</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="calendar-platform">Platform</Label>
                    <Select value={newItemPlatform} onValueChange={setNewItemPlatform}>
                      <SelectTrigger id="calendar-platform">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {platforms.map((platform) => (
                          <SelectItem key={platform.id} value={platform.id}>
                            {platform.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="calendar-keyword">Keyword *</Label>
                    <Input
                      id="calendar-keyword"
                      placeholder="e.g., marathon training tips"
                      value={newItemKeyword}
                      onChange={(e) => setNewItemKeyword(e.target.value)}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="calendar-title">Title (Optional)</Label>
                    <Input
                      id="calendar-title"
                      placeholder="e.g., Complete Marathon Training Guide"
                      value={newItemTitle}
                      onChange={(e) => setNewItemTitle(e.target.value)}
                    />
                  </div>

                  <Button onClick={addCalendarItem} variant="outline" className="w-full">
                    <Plus className="mr-2 h-4 w-4" />
                    Add Item
                  </Button>

                  {/* Content Items List */}
                  {calendarItems.length > 0 && (
                    <div className="space-y-2">
                      <Label>Content Items ({calendarItems.length})</Label>
                      <div className="space-y-2 max-h-64 overflow-auto">
                        {calendarItems.map((item, index) => (
                          <div
                            key={index}
                            className="flex items-center justify-between bg-white border border-gray-200 rounded p-3"
                          >
                            <div className="flex-1">
                              <Badge className="capitalize mb-1">{item.platform}</Badge>
                              <p className="text-sm font-medium">{item.keyword}</p>
                            </div>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => removeCalendarItem(index)}
                            >
                              <X className="h-4 w-4" />
                            </Button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Calendar Settings</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="start-date">Start Date *</Label>
                    <Input
                      id="start-date"
                      type="date"
                      value={startDate}
                      onChange={(e) => setStartDate(e.target.value)}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="duration">Duration (weeks)</Label>
                    <Input
                      id="duration"
                      type="number"
                      min="1"
                      max="52"
                      value={durationWeeks}
                      onChange={(e) => setDurationWeeks(parseInt(e.target.value))}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="frequency">Publishing Frequency</Label>
                    <Select value={frequency} onValueChange={setFrequency}>
                      <SelectTrigger id="frequency">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {frequencies.map((freq) => (
                          <SelectItem key={freq.id} value={freq.id}>
                            {freq.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  {error && activeTab === "calendar" && (
                    <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                      {error}
                    </div>
                  )}

                  <Button onClick={generateCalendar} disabled={loading} className="w-full">
                    {loading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Generating Calendar...
                      </>
                    ) : (
                      <>
                        <Calendar className="mr-2 h-4 w-4" />
                        Generate Calendar
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>
            </div>

            {/* Calendar Display */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Generated Calendar</CardTitle>
                    <CardDescription>
                      {generatedCalendar
                        ? `${generatedCalendar.summary.total_items} items scheduled`
                        : "Calendar will appear here"}
                    </CardDescription>
                  </div>
                  {generatedCalendar && (
                    <Button onClick={exportCalendar} variant="outline" size="sm">
                      <Download className="mr-2 h-4 w-4" />
                      Export CSV
                    </Button>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                {generatedCalendar ? (
                  <div className="space-y-4">
                    {/* Summary */}
                    <div className="bg-blue-50 border border-blue-200 rounded p-4">
                      <h4 className="font-semibold mb-2">Calendar Summary</h4>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <p className="text-gray-600">Total Items</p>
                          <p className="text-2xl font-bold">
                            {generatedCalendar.summary.total_items}
                          </p>
                        </div>
                        <div>
                          <p className="text-gray-600">Duration</p>
                          <p className="text-2xl font-bold">
                            {generatedCalendar.duration_weeks}w
                          </p>
                        </div>
                      </div>
                      <div className="mt-3">
                        <p className="text-gray-600 text-sm mb-1">By Platform</p>
                        <div className="flex flex-wrap gap-2">
                          {Object.entries(generatedCalendar.summary.by_platform).map(
                            ([platform, count]) => (
                              <Badge key={platform} variant="secondary" className="capitalize">
                                {platform}: {count}
                              </Badge>
                            )
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Scheduled Content */}
                    <div>
                      <h4 className="font-semibold mb-3">Scheduled Content</h4>
                      <div className="space-y-2 max-h-[600px] overflow-auto">
                        {generatedCalendar.scheduled_content.map((item, index) => (
                          <div
                            key={index}
                            className="bg-white border border-gray-200 rounded p-3 hover:border-blue-300 transition-colors"
                          >
                            <div className="flex items-start justify-between mb-2">
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-1">
                                  <Badge className="capitalize">{item.platform}</Badge>
                                  <Badge variant="outline">Week {item.week_number}</Badge>
                                </div>
                                <p className="font-medium">{item.title || item.keyword}</p>
                              </div>
                            </div>
                            <div className="flex items-center justify-between text-sm text-gray-600">
                              <span>{formatDate(item.scheduled_date)}</span>
                              <span className="text-xs italic">{item.time_slot_reason}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-12 text-gray-400">
                    <Calendar className="mx-auto h-12 w-12 mb-2" />
                    <p>Add content items and generate calendar</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
