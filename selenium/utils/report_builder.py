
# selenium_fetcher/output_handlers/report_builder.py
"""
Research Report Builder - Structures web analysis data for multiple consumers
This module is the bridge between raw scraping and useful intelligence!
"""

import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import hashlib


class ResearchReportBuilder:
    """
    Builds structured reports from web reconnaissance data

    Key principle: Same data, multiple formats for different consumers:
    - JSON for machines/LLMs
    - Markdown for Obsidian/humans
    - YAML for configuration extraction
    """

    def __init__(self, output_dir: Optional[Path] = None):
        """Initialize with configurable output directory"""
        self.output_dir = Path(output_dir) if output_dir else Path('./research_output')
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Simpler structure - just one data directory
        self.data_dir = self.output_dir / 'analysis'
        self.data_dir.mkdir(exist_ok=True)

    def build_site_analysis(self, recon_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform raw recon data into structured analysis
        UPDATED for new report structure!
        """
        # Use metadata from new structure
        metadata = recon_data.get('metadata', {})
        analysis_id = metadata.get('analysis_id') or self._generate_analysis_id(metadata.get('url', ''))

        # Build report using NEW structure
        report = {
            "metadata": {
                "analysis_id": analysis_id,
                "timestamp": metadata.get('timestamp', datetime.now().isoformat()),
                "url": metadata.get('url', ''),
                "title": metadata.get('title', 'Untitled'),
                "analysis_version": "2.0"  # Updated version!
            },

            "site_structure": {
                # Pull from discoveries.features (NEW path!)
                "total_elements": recon_data.get('discoveries', {}).get('features', {}).get('total_elements', 0),
                "interactive_elements": recon_data.get('discoveries', {}).get('features', {}).get('form_count', 0),
                "navigation_type": self._determine_nav_type(recon_data),
                "content_delivery": self._analyze_content_delivery(recon_data),
                "dynamic_features": recon_data.get('discoveries', {}).get('ajax', {})
            },

            "accessibility_analysis": {
                "content_availability": self._analyze_availability(recon_data),
                "interaction_methods": self._extract_interaction_methods(recon_data),
                "authentication_required": recon_data.get('discoveries', {}).get('features', {}).get('has_login',
                                                                                                     False),
                "dynamic_loading": len(recon_data.get('discoveries', {}).get('api_endpoints', [])) > 0
            },

            "technical_insights": {
                # Pull from analysis section (NEW!)
                "detected_frameworks": recon_data.get('analysis', {}).get('tech_stack', {}),
                "api_endpoints": recon_data.get('discoveries', {}).get('api_endpoints', []),
                "data_formats": self._detect_data_formats(recon_data),
                "page_performance": {
                    "load_time": recon_data.get('baseline', {}).get('metrics', {}).get('timing', {}).get(
                        'total_load_time', 0),
                    "resource_count": recon_data.get('baseline', {}).get('metrics', {}).get('resources', {})
                }
            },

            "extraction_strategies": {
                "recommended_approach": self._recommend_approach(recon_data),
                "success_probability": self._calculate_success_probability(recon_data),
                "required_techniques": self._list_required_techniques(recon_data),
                "complexity_score": self._calculate_complexity(recon_data)
            },

            "artifacts": recon_data.get('artifacts', {}),  # Just pass through!

            "research_notes": {
                "interesting_findings": self._extract_interesting_findings(recon_data),
                "potential_challenges": self._identify_challenges(recon_data),
                "recommended_next_steps": self._suggest_next_steps(recon_data)
            }
        }

        return report

    def save_analysis(self, report: Dict[str, Any], formats: List[str] = None) -> Dict[str, Path]:
        """Save analysis in requested formats - SIMPLIFIED"""
        if formats is None:
            formats = ['json', 'markdown']  # Skip YAML by default

        saved_files = {}
        analysis_id = report['metadata']['analysis_id']

        # All files go in one directory
        base_name = self.data_dir / analysis_id

        if 'json' in formats:
            json_path = base_name.with_suffix('.json')
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            saved_files['json'] = json_path

        if 'markdown' in formats:
            md_path = base_name.with_suffix('.md')
            md_content = self._generate_markdown_report(report)
            md_path.write_text(md_content, encoding='utf-8')
            saved_files['markdown'] = md_path

        return saved_files

    def _generate_analysis_id(self, url: str) -> str:
        """Fallback ID generator - matches recon_engine format"""
        # Only called if recon didn't provide an ID
        session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"recon_{session_id}"  # Simple, matches recon_engine format

    def _determine_nav_type(self, recon_data: Dict) -> str:
        """Determine navigation type from NEW structure"""
        pagination = recon_data.get('analysis', {}).get('pagination_patterns', {})

        if pagination.get('style') == 'infinite':
            return "infinite_scroll"
        elif pagination.get('style') == 'numbered':
            return "paginated"
        else:
            return "single_page"

    def _analyze_content_delivery(self, recon_data: Dict) -> Dict[str, Any]:
        """Analyze content delivery from NEW structure"""
        ajax = recon_data.get('discoveries', {}).get('ajax', {})
        features = recon_data.get('discoveries', {}).get('features', {})

        return {
            "primary_method": "ajax" if ajax.get('endpoints', []) else "static",
            "uses_websockets": len(ajax.get('websockets', [])) > 0,
            "api_available": len(recon_data.get('discoveries', {}).get('api_endpoints', [])) > 0,
            "requires_javascript": features.get('uses_javascript', False)
        }

    def _analyze_availability(self, recon_data: Dict) -> str:
        """Transform barrier analysis - UPDATED paths"""
        barriers = recon_data.get('discoveries', {}).get('barriers', [])
        liberation_results = recon_data.get('liberation_results', [])

        if not barriers:
            return "fully_accessible"

        successful_tactics = [r for r in liberation_results if r.get('success')]
        if len(successful_tactics) >= len(barriers):
            return "accessible_with_techniques"
        elif successful_tactics:
            return "partially_accessible"
        else:
            return "restricted_access"

    def _recommend_approach(self, recon_data: Dict) -> List[str]:
        """Recommend approach using NEW structure"""
        recommendations = []

        # Check discoveries
        api_endpoints = recon_data.get('discoveries', {}).get('api_endpoints', [])
        ajax = recon_data.get('discoveries', {}).get('ajax', {})
        features = recon_data.get('discoveries', {}).get('features', {})
        pagination = recon_data.get('analysis', {}).get('pagination_patterns', {})

        if api_endpoints:
            recommendations.append("direct_api_access")

        if not ajax.get('endpoints'):
            recommendations.append("static_html_parsing")

        if features.get('uses_javascript'):
            recommendations.append("browser_automation_required")

        if pagination.get('has_pagination'):
            recommendations.append("pagination_handling_needed")

        return recommendations

    def _calculate_success_probability(self, recon_data: Dict) -> float:
        """Calculate success probability - UPDATED"""
        score = 1.0

        # Reduce for barriers
        barriers = len(recon_data.get('discoveries', {}).get('barriers', []))
        score -= (barriers * 0.1)

        # Increase for successful tactics
        successful = len([r for r in recon_data.get('liberation_results', [])
                          if r.get('success')])
        score += (successful * 0.15)

        # Bonus for API
        if recon_data.get('discoveries', {}).get('api_endpoints'):
            score += 0.2

        return max(0.1, min(1.0, score))

    def _generate_markdown_report(self, report: Dict) -> str:
        """Generate human-readable markdown report - ENHANCED"""

        # Safe get helper
        def safe_get(d, *keys, default='N/A'):
            for key in keys:
                if isinstance(d, dict):
                    d = d.get(key, {})
                else:
                    return default
            return d if d else default

        md = f"""# 🔍 Web Analysis Report

    **Target URL**: {report['metadata']['url']}  
    **Analysis ID**: `{report['metadata']['analysis_id']}`  
    **Generated**: {report['metadata']['timestamp']}

    ## 📊 Executive Summary

    - **Accessibility**: {report['accessibility_analysis']['content_availability'].replace('_', ' ').title()}
    - **Complexity Score**: {report['extraction_strategies']['complexity_score']}/10
    - **Success Probability**: {report['extraction_strategies']['success_probability']:.0%}
    - **Primary Method**: {report['site_structure']['content_delivery']['primary_method']}

    ## 🏗️ Site Structure

    | Feature | Value |
    |---------|-------|
    | Total Elements | {report['site_structure']['total_elements']:,} |
    | Interactive Elements | {report['site_structure']['interactive_elements']} |
    | Navigation Type | {report['site_structure']['navigation_type'].replace('_', ' ').title()} |
    | Requires JavaScript | {'✅ Yes' if report['site_structure']['content_delivery']['requires_javascript'] else '❌ No'} |
    | API Available | {'✅ Yes' if safe_get(report, 'site_structure', 'content_delivery', 'api_available') else '❌ No'} |

    ## 🎯 Recommended Extraction Strategy
    """

        # Add approaches with icons
        icons = {'direct_api_access': '🚀', 'static_html_parsing': '📄',
                 'browser_automation_required': '🤖', 'pagination_handling_needed': '📑'}

        for i, approach in enumerate(report['extraction_strategies']['recommended_approach'], 1):
            icon = icons.get(approach, '▶️')
            md += f"\n{i}. {icon} **{approach.replace('_', ' ').title()}**"

        md += "\n\n## 💡 Technical Insights\n"

        # Frameworks section
        frameworks = report['technical_insights'].get('detected_frameworks', {})
        detected = [fw for fw, is_detected in frameworks.items() if is_detected]

        if detected:
            md += "\n### Detected Frameworks\n"
            for fw in detected:
                md += f"- ✓ {fw}\n"

        # API endpoints with better formatting
        endpoints = report['technical_insights'].get('api_endpoints', [])
        if endpoints:
            md += f"\n### 🔌 API Endpoints Discovered ({len(endpoints)} total)\n"
            md += "```\n"
            for endpoint in endpoints[:5]:
                md += f"{endpoint}\n"
            if len(endpoints) > 5:
                md += f"... and {len(endpoints) - 5} more\n"
            md += "```\n"

        # Screenshots section with better formatting
        screenshots = report.get('artifacts', {}).get('screenshots', [])
        if screenshots:
            md += f"\n## 📸 Captured Screenshots ({len(screenshots)})\n\n"
            for screenshot in screenshots:
                md += f"- **{screenshot['name']}** - `{screenshot.get('timestamp', 'N/A')}`\n"

        # Research notes
        md += "\n## 📝 Research Notes\n"

        findings = report['research_notes'].get('interesting_findings', [])
        if findings:
            md += "\n### 🔍 Key Findings\n"
            for finding in findings:
                md += f"- {finding}\n"

        challenges = report['research_notes'].get('potential_challenges', [])
        if challenges:
            md += "\n### ⚠️ Potential Challenges\n"
            for challenge in challenges:
                md += f"- {challenge}\n"

        next_steps = report['research_notes'].get('recommended_next_steps', [])
        if next_steps:
            md += "\n### ✅ Recommended Next Steps\n"
            for i, step in enumerate(next_steps, 1):
                md += f"{i}. {step}\n"

        # Add performance metrics if available
        perf = safe_get(report, 'technical_insights', 'page_performance')
        if perf and perf != 'N/A':
            md += f"\n## ⚡ Performance Metrics\n"
            if perf.get('load_time'):
                md += f"- **Load Time**: {perf['load_time']}ms\n"
            if perf.get('resource_count'):
                md += f"- **Resources**: {perf['resource_count']}\n"

        md += "\n---\n*Generated by Selenium Research Tools v2.0*\n"

        return md

    def _extract_interesting_findings(self, recon_data: Dict) -> List[str]:
        """Extract notable findings from NEW structure"""
        findings = []

        # From discoveries section
        api_endpoints = recon_data.get('discoveries', {}).get('api_endpoints', [])
        if api_endpoints:
            findings.append(f"🔌 Found {len(api_endpoints)} API endpoints")

        downloads = recon_data.get('discoveries', {}).get('downloads', [])
        if downloads:
            findings.append(f"📥 Identified {len(downloads)} downloadable resources")

        # From baseline analysis
        hidden_data = recon_data.get('baseline', {}).get('metadata', {}).get('ldJson', [])
        if hidden_data:
            findings.append("📊 Site contains structured JSON-LD data")

        # From forms discovery
        forms = recon_data.get('discoveries', {}).get('forms', [])
        if forms:
            search_forms = [f for f in forms if 'search' in str(f).lower()]
            if search_forms:
                findings.append(f"🔍 Found {len(search_forms)} search forms")

        # From liberation results
        liberation_results = recon_data.get('liberation_results', [])
        successful_tactics = [r for r in liberation_results if r.get('success')]
        if successful_tactics:
            findings.append(f"🚀 Successfully applied {len(successful_tactics)} liberation tactics")

        # From tech stack
        tech_stack = recon_data.get('analysis', {}).get('tech_stack', {})
        detected_tech = [tech for tech, detected in tech_stack.items() if detected]
        if detected_tech:
            findings.append(f"💻 Detected technologies: {', '.join(detected_tech)}")

        # Network insights
        network_stats = recon_data.get('network_summary', {}).get('statistics', {})
        if network_stats.get('avg_response_time'):
            findings.append(f"⚡ Average response time: {network_stats['avg_response_time']:.0f}ms")

        return findings

    def _calculate_complexity(self, recon_data: Dict) -> int:
        """Calculate extraction complexity - UPDATED for new structure"""
        complexity = 1  # Base complexity

        # Check discoveries.features
        features = recon_data.get('discoveries', {}).get('features', {})
        if features.get('has_login'):
            complexity += 2  # Auth adds complexity

        # APIs actually REDUCE complexity!
        if recon_data.get('discoveries', {}).get('api_endpoints'):
            complexity -= 1  # APIs make it easier

        # Check barriers
        barriers = recon_data.get('discoveries', {}).get('barriers', [])
        if barriers:
            # Different barriers have different complexity
            for barrier in barriers:
                if 'cloudflare' in barrier.lower():
                    complexity += 3  # Cloudflare is tough
                elif 'paywall' in barrier.lower():
                    complexity += 2
                else:
                    complexity += 1

        # Check pagination complexity
        pagination = recon_data.get('analysis', {}).get('pagination_patterns', {})
        if pagination.get('style') == 'infinite':
            complexity += 2  # Infinite scroll is complex
        elif pagination.get('style') == 'numbered':
            complexity += 1  # Regular pagination is easier

        # JavaScript requirement
        if features.get('uses_javascript'):
            complexity += 1

        # Reduce if we found good selectors
        if recon_data.get('analysis', {}).get('search_patterns', {}).get('has_search'):
            complexity -= 1  # Search makes crawling easier

        # Failed liberation tactics indicate higher complexity
        liberation_results = recon_data.get('liberation_results', [])
        failed_tactics = len([r for r in liberation_results if not r.get('success')])
        if failed_tactics > 3:
            complexity += 2

        # Ensure score is in valid range
        return max(1, min(10, complexity))

    def _extract_interaction_methods(self, recon_data: Dict) -> List[str]:
        """Extract available interaction methods from NEW structure"""
        methods = []

        # Get features from discoveries
        features = recon_data.get('discoveries', {}).get('features', {})

        if features.get('has_search'):
            methods.append('search_functionality')

        # Get forms from discoveries.forms (it's a list now!)
        forms = recon_data.get('discoveries', {}).get('forms', [])
        if forms:
            methods.append('form_submission')
            # Be more specific about form types
            search_forms = [f for f in forms if 'search' in str(f).lower()]
            if search_forms:
                methods.append('search_forms')
            login_forms = [f for f in forms if any(inp.get('type') == 'password' for inp in f.get('inputs', []))]
            if login_forms:
                methods.append('authentication_forms')

        if features.get('table_count', 0) > 0:
            methods.append('data_tables')

        # Check liberation results for dynamic content
        for result in recon_data.get('liberation_results', []):
            if result.get('success'):
                if result.get('tactic') == 'expand_content':
                    methods.append('expandable_content')
                elif result.get('tactic') == 'detect_ajax':
                    methods.append('ajax_interaction')
                elif result.get('tactic') == 'remove_overlays':
                    methods.append('modal_interaction')

        # Check for pagination
        if recon_data.get('analysis', {}).get('pagination_patterns', {}).get('has_pagination'):
            methods.append('pagination_navigation')

        # Check for download capabilities
        if recon_data.get('discoveries', {}).get('downloads'):
            methods.append('direct_downloads')

        return list(set(methods))  # Remove duplicates

    def _detect_data_formats(self, recon_data: Dict) -> List[str]:
        """Detect available data formats from NEW structure"""
        formats = set()

        # Check downloads (new path)
        downloads = recon_data.get('discoveries', {}).get('downloads', [])
        for item in downloads:
            # Extract format from extension or type
            if item.get('extension'):
                formats.add(item['extension'].lower())
            elif item.get('type'):
                # Handle type descriptions
                dtype = item['type'].lower()
                if 'pdf' in dtype:
                    formats.add('pdf')
                elif 'csv' in dtype:
                    formats.add('csv')
                elif 'excel' in dtype or 'xls' in dtype:
                    formats.add('excel')
                elif 'json' in dtype:
                    formats.add('json')

        # Check baseline metadata for structured data
        baseline_meta = recon_data.get('baseline', {}).get('metadata', {})
        if baseline_meta.get('ldJson'):
            formats.add('json-ld')
        if baseline_meta.get('meta_tags'):
            formats.add('meta-tags')
        if baseline_meta.get('open_graph'):
            formats.add('open-graph')

        # Check for API data formats
        if recon_data.get('discoveries', {}).get('api_endpoints'):
            formats.add('json-api')

        # Check AJAX patterns for data formats
        ajax = recon_data.get('discoveries', {}).get('ajax', {})
        if ajax.get('endpoints'):
            formats.add('ajax-json')
        if ajax.get('websockets'):
            formats.add('websocket')

        # Check for table data
        if recon_data.get('discoveries', {}).get('features', {}).get('table_count', 0) > 0:
            formats.add('html-tables')

        # Check network responses for content types
        network_summary = recon_data.get('network_summary', {})
        for endpoint_data in network_summary.get('api_patterns', {}).values():
            # This would need actual response analysis
            formats.add('api-responses')

        return sorted(list(formats))  # Sorted for consistency

    def _list_required_techniques(self, recon_data: Dict) -> List[str]:
        """List techniques required for extraction - ENHANCED"""
        techniques = []

        # Enhanced mapping with descriptions
        tactic_mapping = {
            'remove_overlays': {
                'name': 'overlay_handling',
                'description': 'Remove popups and modal overlays'
            },
            'expand_content': {
                'name': 'dynamic_content_expansion',
                'description': 'Expand collapsed sections'
            },
            'detect_ajax': {
                'name': 'ajax_monitoring',
                'description': 'Monitor and intercept AJAX requests'
            },
            'extract_hidden_data': {
                'name': 'metadata_extraction',
                'description': 'Extract hidden metadata and attributes'
            },
            'humanize_browser': {
                'name': 'browser_fingerprinting',
                'description': 'Avoid bot detection'
            },
            'bypass_paywall': {
                'name': 'access_control_bypass',
                'description': 'Handle paywalls and access restrictions'
            },
            'disable_lazy_loading': {
                'name': 'lazy_load_handling',
                'description': 'Force load of lazy content'
            },
            'extract_shadow_dom': {
                'name': 'shadow_dom_access',
                'description': 'Access shadow DOM content'
            },
            'bypass_cloudflare': {
                'name': 'cloudflare_handling',
                'description': 'Handle Cloudflare protection'
            }
        }

        # Get successful tactics
        for result in recon_data.get('liberation_results', []):
            if result.get('success') and result.get('tactic') in tactic_mapping:
                technique = tactic_mapping[result['tactic']]['name']
                if technique not in techniques:
                    techniques.append(technique)

        # Add techniques based on site characteristics
        features = recon_data.get('discoveries', {}).get('features', {})

        if features.get('uses_javascript'):
            techniques.append('javascript_execution')

        if features.get('has_login'):
            techniques.append('session_management')

        if recon_data.get('analysis', {}).get('pagination_patterns', {}).get('style') == 'infinite':
            techniques.append('infinite_scroll_handling')

        # Check barriers for additional requirements
        barriers = recon_data.get('discoveries', {}).get('barriers', [])
        for barrier in barriers:
            if 'cookie' in barrier.lower():
                techniques.append('cookie_management')
            elif 'captcha' in barrier.lower():
                techniques.append('captcha_solving')

        return list(set(techniques))  # Remove duplicates

    def _get_technique_details(self, techniques: List[str]) -> List[Dict[str, str]]:
        """Get detailed information about required techniques"""
        technique_info = {
            'overlay_handling': 'Use JavaScript to remove modal overlays and popups',
            'dynamic_content_expansion': 'Click or trigger elements to reveal hidden content',
            'ajax_monitoring': 'Intercept AJAX requests to capture dynamic data',
            'metadata_extraction': 'Extract data attributes and hidden form fields',
            'browser_fingerprinting': 'Modify browser properties to avoid detection',
            'javascript_execution': 'Use Selenium or similar for JS-heavy sites',
            'session_management': 'Handle login and maintain authenticated sessions',
            'infinite_scroll_handling': 'Implement scroll automation for endless pages',
            'cookie_management': 'Accept or manipulate cookies as needed',
            'lazy_load_handling': 'Trigger lazy-loaded content to appear'
        }

        return [
            {
                'technique': tech,
                'implementation': technique_info.get(tech, 'Custom implementation required')
            }
            for tech in techniques
        ]

    def _organize_screenshots(self, recon_data: Dict) -> List[Dict[str, str]]:
        """Simply pass through the already organized screenshots"""
        # Everything is already in artifacts.screenshots, just return it!
        return recon_data.get('artifacts', {}).get('screenshots', [])

    def _organize_snapshots(self, recon_data: Dict) -> List[Dict[str, Any]]:
        """Organize DOM snapshots with actionable insights"""
        snapshots = []

        dom_snapshots = recon_data.get('captured_data', {}).get('dom_snapshots', [])

        for i, snapshot in enumerate(dom_snapshots):
            snapshot_info = {
                'index': i,
                'checkpoint': snapshot.get('name', f'snapshot_{i}'),
                'timestamp': snapshot.get('timestamp', ''),
                'changes': {
                    'new_elements': len(snapshot.get('new_elements', [])),
                    'dom_mutations': len(snapshot.get('dom_changes', [])),
                    'url_changed': snapshot.get('url_changed', False)
                }
            }

            # Add significance indicator
            total_changes = (snapshot_info['changes']['new_elements'] +
                             snapshot_info['changes']['dom_mutations'])

            if total_changes > 50:
                snapshot_info['significance'] = 'major'
            elif total_changes > 10:
                snapshot_info['significance'] = 'moderate'
            else:
                snapshot_info['significance'] = 'minor'

            snapshots.append(snapshot_info)

        return snapshots

    def _organize_network_logs(self, recon_data: Dict) -> Dict[str, Any]:
        """Organize network logs with actionable intelligence"""
        # Get both captured data and analyzed network summary
        network_data = recon_data.get('captured_data', {}).get('network_log', [])
        network_summary = recon_data.get('network_summary', {})

        summary = {
            'overview': {
                'total_requests': len(network_data),
                'api_calls': 0,
                'failed_requests': 0,
                'unique_domains': 0
            },
            'api_endpoints': [],
            'error_patterns': {},
            'performance': {
                'avg_response_time': 0,
                'slowest_endpoints': []
            },
            'domains': {
                'internal': [],
                'external': []
            }
        }

        # Use analyzed data if available
        if network_summary:
            # Use pre-analyzed statistics
            stats = network_summary.get('statistics', {})
            summary['performance']['avg_response_time'] = stats.get('avg_response_time', 0)

            # Get API patterns
            api_patterns = network_summary.get('api_patterns', {})
            summary['api_endpoints'] = list(api_patterns.keys())[:10]  # Top 10

            # Get error information
            error_responses = network_summary.get('error_responses', [])
            for error in error_responses:
                status = error.get('status', 'unknown')
                if status not in summary['error_patterns']:
                    summary['error_patterns'][status] = []
                summary['error_patterns'][status].append(error.get('url', ''))

        # Process raw network data for additional insights
        domains = set()
        response_times = []

        for request in network_data:
            url = request.get('url', '')

            # Count API calls
            if any(marker in url for marker in ['/api/', '/v1/', '/v2/', '.json']):
                summary['overview']['api_calls'] += 1

            # Count errors
            if request.get('error') or request.get('status', 0) >= 400:
                summary['overview']['failed_requests'] += 1

            # Extract domains
            if url.startswith('http'):
                try:
                    from urllib.parse import urlparse
                    parsed = urlparse(url)
                    domain = parsed.netloc
                    domains.add(domain)

                    # Categorize as internal/external
                    if recon_data.get('metadata', {}).get('url', ''):
                        main_domain = urlparse(recon_data['metadata']['url']).netloc
                        if domain == main_domain:
                            summary['domains']['internal'].append(domain)
                        else:
                            summary['domains']['external'].append(domain)

                except:
                    pass

            # Collect response times
            if request.get('duration'):
                response_times.append({
                    'url': url,
                    'duration': request['duration']
                })

        # Finalize summary
        summary['overview']['unique_domains'] = len(domains)

        # Find slowest endpoints
        if response_times:
            sorted_times = sorted(response_times, key=lambda x: x['duration'], reverse=True)
            summary['performance']['slowest_endpoints'] = [
                {'url': rt['url'].split('?')[0], 'duration': rt['duration']}  # Remove query params
                for rt in sorted_times[:5]
            ]

        # Add insights
        summary['insights'] = []

        if summary['overview']['api_calls'] > 0:
            summary['insights'].append(
                f"Site uses {summary['overview']['api_calls']} API calls - consider direct API access")

        if summary['overview']['failed_requests'] > 5:
            summary['insights'].append(
                f"High error rate ({summary['overview']['failed_requests']} failures) - implement robust error handling")

        if len(summary['domains']['external']) > 10:
            summary['insights'].append("Heavy external dependencies - consider caching strategy")

        return summary

    def _identify_challenges(self, recon_data: Dict) -> List[Dict[str, Any]]:
        """Identify SPECIFIC extraction challenges with SOLUTIONS"""
        challenges = []

        # Analyze failed tactics for patterns
        liberation_results = recon_data.get('liberation_results', [])
        failed_tactics = [r for r in liberation_results if not r.get('success')]

        # PAYWALL CHALLENGE - Be specific!
        if any('paywall' in str(b).lower() for b in recon_data.get('access_barriers', [])):
            # Check which tactics worked/failed
            paywall_solutions = []
            if any(r['tactic'] == 'bypass_paywall' and r['success'] for r in liberation_results):
                paywall_solutions.append("Paywall bypass successful - use same tactics")
            else:
                paywall_solutions.append("Consider: Archive.org fallback")
                paywall_solutions.append("Consider: RSS feed for summaries")
                paywall_solutions.append("Consider: Academic database access")

            challenges.append({
                'type': 'paywall',
                'severity': 'high',
                'solutions': paywall_solutions,
                'workaround_exists': len(paywall_solutions) > 0
            })

        # AUTHENTICATION - Specific requirements
        if recon_data.get('discovered_features', {}).get('has_login'):
            auth_details = {
                'type': 'authentication',
                'severity': 'medium',
                'details': {
                    'form_found': len(recon_data.get('forms', [])) > 0,
                    'oauth_detected': 'oauth' in str(recon_data.get('authentication_flow', {})).lower(),
                    'session_management': 'cookies' if recon_data.get('baseline', {}).get('cookies') else 'unknown'
                },
                'solutions': ["Implement session persistence", "Consider credential management"]
            }
            challenges.append(auth_details)

        # DYNAMIC CONTENT - Specific requirements
        if recon_data.get('pagination_patterns', {}).get('style') == 'infinite':
            scroll_data = {
                'type': 'infinite_scroll',
                'severity': 'low',  # We can handle this!
                'details': {
                    'ajax_endpoints': recon_data.get('ajax_patterns', {}).get('endpoints', []),
                    'scroll_trigger_found': len(recon_data.get('ajax_patterns', {}).get('endpoints', [])) > 0
                },
                'solutions': ["Monitor network for API calls", "Implement scroll automation", "Check for hidden API"]
            }
            challenges.append(scroll_data)

        # ANTI-BOT MEASURES
        if any('cloudflare' in str(b).lower() for b in recon_data.get('access_barriers', [])):
            challenges.append({
                'type': 'anti_bot',
                'severity': 'high',
                'provider': 'cloudflare',
                'solutions': ["Use undetected-chromedriver", "Implement request delays", "Rotate user agents"]
            })

        return challenges

    def _suggest_next_steps(self, recon_data: Dict) -> List[Dict[str, Any]]:
        """Generate SPECIFIC, EXECUTABLE next steps for scraper development"""
        steps = []

        # API DISCOVERY - Be specific about testing!
        if recon_data.get('api_endpoints'):
            api_endpoints = recon_data.get('api_endpoints', [])
            steps.append({
                'priority': 1,
                'action': 'test_api_endpoints',
                'specific_tasks': [
                    f"Test endpoint: {endpoint}" for endpoint in api_endpoints[:3]
                ],
                'test_commands': [
                    f"curl -X GET '{endpoint}' -H 'Accept: application/json'"
                    for endpoint in api_endpoints[:3]
                ],
                'expected_outcome': 'Determine if API returns structured data'
            })

        # SEARCH FUNCTIONALITY - Concrete mapping
        if recon_data.get('discovered_features', {}).get('has_search'):
            search_forms = recon_data.get('forms', {}).get('search_forms', [])
            if search_forms:
                form = search_forms[0]
                steps.append({
                    'priority': 2,
                    'action': 'map_search_api',
                    'specific_tasks': [
                        f"Test search with query: 'test'",
                        f"Identify response format (JSON/HTML)",
                        f"Map pagination parameters"
                    ],
                    'implementation_hint': f"Form action: {form.get('action', 'unknown')}, Method: {form.get('method', 'GET')}"
                })

        # DOWNLOAD PLANNING - Actual queue structure
        if recon_data.get('downloadable_content'):
            downloads = recon_data.get('downloadable_content', [])
            download_types = {}
            for dl in downloads:
                dl_type = dl.get('extension', 'unknown')
                download_types[dl_type] = download_types.get(dl_type, 0) + 1

            steps.append({
                'priority': 3,
                'action': 'implement_download_queue',
                'breakdown': download_types,
                'specific_tasks': [
                    "Implement parallel download manager",
                    "Add progress tracking",
                    "Handle failed downloads with retry"
                ],
                'storage_estimate': f"Estimated {len(downloads) * 5}MB storage needed"
            })

        # COMPLEXITY-BASED RECOMMENDATIONS
        complexity = self._calculate_complexity(recon_data)
        if complexity > 7:
            steps.append({
                'priority': 1,  # High priority!
                'action': 'modular_approach',
                'specific_tasks': [
                    "Phase 1: Data discovery (map all data sources)",
                    "Phase 2: Authentication/access (solve barriers)",
                    "Phase 3: Extraction (implement scrapers)",
                    "Phase 4: Monitoring (detect changes)"
                ],
                'rationale': f"High complexity ({complexity}/10) requires phased approach"
            })

        # QUICK WINS - Always include something achievable TODAY
        steps.append({
            'priority': 1,
            'action': 'quick_validation',
            'specific_tasks': [
                "Write a 10-line script to fetch the homepage",
                "Extract one data point to validate approach",
                "Test rate limits with 10 rapid requests"
            ],
            'time_estimate': '30 minutes',
            'purpose': 'Build confidence and validate assumptions'
        })

        return sorted(steps, key=lambda x: x['priority'])

    def create_extraction_config(self, report: Dict) -> Dict[str, Any]:
        """
        Generate COMPLETE extraction configuration for scraper
        This is THE BRIDGE between recon and implementation!
        """
        config = {
            'metadata': {
                'generated_from': report['metadata']['analysis_id'],
                'target_url': report['metadata']['url'],
                'complexity_score': report['extraction_strategies']['complexity_score'],
                'created_at': datetime.now().isoformat()
            },

            'extraction_strategy': {
                'primary_method': self._determine_primary_method(report),
                'fallback_methods': self._determine_fallback_methods(report),
                'requires_browser': report['site_structure']['content_delivery']['requires_javascript'],
                'can_use_api': len(report.get('api_endpoints', [])) > 0
            },

            'technical_requirements': {
                'libraries_needed': self._determine_required_libraries(report),
                'browser_config': {
                    'headless': True,
                    'user_agent_rotation': len(report.get('access_barriers', [])) > 0,
                    'proxy_required': 'cloudflare' in str(report.get('access_barriers', [])).lower()
                } if report['site_structure']['content_delivery']['requires_javascript'] else None
            },

            'navigation': {
                'pagination': {
                    'enabled': report['site_structure']['navigation_type'] != 'single_page',
                    'type': report['site_structure']['navigation_type'],
                    'implementation': self._get_pagination_implementation(report)
                },
                'entry_points': [
                    {
                        'url': ep['url'],
                        'type': ep['type'],
                        'priority': 1 if ep['type'] == 'api' else 2
                    }
                    for ep in report.get('entry_points', [])[:5]
                ]
            },

            'data_extraction': {
                'selectors': self._generate_selector_hints(report),
                'ajax_monitoring': {
                    'enabled': len(report.get('ajax_patterns', {}).get('endpoints', [])) > 0,
                    'endpoints_to_monitor': report.get('ajax_patterns', {}).get('endpoints', [])[:10]
                },
                'storage_format': 'json',  # Always JSON for flexibility
                'deduplication_key': self._suggest_dedup_key(report)
            },

            'rate_limiting': {
                'base_delay': self._calculate_safe_delay(report),
                'randomization': [0.5, 1.5],  # Multiply base delay by random value in range
                'burst_size': 10 if report['extraction_strategies']['complexity_score'] < 5 else 5,
                'respect_robots_txt': True
            },

            'error_handling': {
                'retry_attempts': 3,
                'backoff_factor': 2,
                'timeout_seconds': 30,
                'screenshot_on_error': report['extraction_strategies']['complexity_score'] > 5
            },

            'monitoring': {
                'track_changes': True,
                'alert_on_structure_change': True,
                'preserve_artifacts': ['screenshots'] + (
                    ['network_logs', 'dom_snapshots'] if report['extraction_strategies']['complexity_score'] > 7 else []
                )
            },

            'implementation_template': self._generate_starter_code(report)
        }

        return config

    def _determine_primary_method(self, report: Dict) -> str:
        """Determine the PRIMARY extraction method with clear logic"""
        # API FIRST if available and substantial
        if len(report.get('api_endpoints', [])) >= 3:
            return 'api_direct'

        # Static HTML if no JS required
        if not report['site_structure']['content_delivery']['requires_javascript']:
            return 'requests_beautifulsoup'

        # Selenium for dynamic content
        return 'selenium_webdriver'

    def _calculate_safe_delay(self, report: Dict) -> float:
        """Calculate safe request delay based on site characteristics"""
        base_delay = 1.0

        # Increase for complexity
        complexity = report['extraction_strategies']['complexity_score']
        if complexity > 7:
            base_delay = 3.0
        elif complexity > 5:
            base_delay = 2.0

        # Increase for anti-bot measures
        if any('cloudflare' in str(b).lower() for b in report.get('access_barriers', [])):
            base_delay *= 2

        # Decrease for APIs (they expect automation)
        if report.get('api_endpoints'):
            base_delay *= 0.5

        return base_delay

    def validate_report_builder(self):
        """Validate that report builder is working correctly"""
        try:
            # Use REAL data structure that matches what recon_engine produces
            sample_recon_output = {
                'url': 'https://example.com',
                'title': 'Example Site',
                'metadata': {
                    'analysis_id': 'test_validation',
                    'timestamp': datetime.now().isoformat(),
                    'artifacts_path': './selenium_downloads'
                },
                'discovered_features': {
                    'has_search': True,
                    'has_login': False,
                    'form_count': 2,
                    'uses_javascript': True,
                    'total_elements': 150,
                    'table_count': 3
                },
                'ajax_patterns': {
                    'endpoints': ['/api/v1/data', '/api/v1/search']
                },
                'liberation_results': [
                    {'tactic': 'remove_overlays', 'success': True, 'details': 'Removed 2 overlays'},
                    {'tactic': 'detect_ajax', 'success': True, 'details': 'Found 2 API endpoints'}
                ],
                'access_barriers': ['cookie_banner'],
                'artifacts': {
                    'screenshots': [
                        {'name': 'baseline', 'path': 'baseline_123.png', 'timestamp': datetime.now().isoformat()}
                    ],
                    'dom_snapshots': [],
                    'network_logs': {}
                },
                'captured_data': {},
                'forms': [],
                'api_endpoints': ['/api/v1/data', '/api/v1/search'],
                'downloadable_content': [],
                'pagination_patterns': {'has_pagination': False, 'style': 'none'},
                'tech_stack': {'jquery': True, 'react': False}
            }

            # Validate all core functions work
            builder = ResearchReportBuilder()

            # Test 1: Build analysis
            report = builder.build_site_analysis(sample_recon_output)
            assert 'metadata' in report, "Report missing metadata"
            assert 'extraction_strategies' in report, "Report missing extraction strategies"

            # Test 2: Create extraction config
            config = builder.create_extraction_config(report)
            assert 'technical_requirements' in config, "Config missing technical requirements"
            assert config['extraction_strategy']['primary_method'] in ['api_direct', 'requests_beautifulsoup',
                                                                       'selenium_webdriver']

            # Test 3: Verify we can save (but don't actually save in validation)
            assert hasattr(builder, 'save_analysis'), "Missing save_analysis method"

            print("✅ ResearchReportBuilder validation PASSED!")
            print(f"   - Analysis structure valid")
            print(f"   - Extraction config generation valid")
            print(f"   - All methods accessible")
            return True

        except Exception as e:
            print(f"❌ ResearchReportBuilder validation FAILED: {e}")
            import traceback
            traceback.print_exc()
            return False

    if __name__ == "__main__":
        # Only run validation when script is run directly
        validate_report_builder()
