# selenium_fetcher/fetchers/recon_engine.py
import re
import shutil
from pathlib import Path

import yaml

from selenium_fetcher.base_fetcher import BaseFetcher
from selenium_fetcher.toolkit import Toolkit  # Import our toolkit!
from selenium.webdriver.common.by import By
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional


class ReconEngine(BaseFetcher):
    """
    Reconnaissance engine that uses shared toolkit for liberation tactics
    """

    def __init__(self, config=None):
        super().__init__(config)
        self.toolkit = Toolkit()
        self.current_task = None  # Add this!
        self.captured_data = {
            'dom_snapshots': [],
            'network_log': [],
            'javascript_states': [],
            'metadata_timeline': []
        }

    def scout_site(self, url: str, safe_mode: bool = False) -> Any | None:
        """Scout using tactics from the toolkit - FIXED SCREENSHOT TRACKING"""

        mode = "safe" if safe_mode else "LIBERATION"
        self.logger.info(f"[RECON] MISSION: {url} (Mode: {mode})")

        self._setup_comprehensive_monitoring()

        if not self.go_to_url(url):
            return None

        report = self._initialize_report(url, mode)
        report['title'] = self.driver.title

        # CRITICAL: Store the artifacts base path in the report!
        report['metadata']['artifacts_path'] = str(self.base_path)

        # Take baseline screenshot - FIXED PATH HANDLING
        self.logger.info("[CAPTURE] Capturing baseline data...")
        baseline_screenshot = self.take_screenshot("baseline")

        # Store absolute path consistently
        if baseline_screenshot:
            baseline_screenshot_path = str(baseline_screenshot.absolute())

            # Initialize artifacts if not exists
            if 'artifacts' not in report:
                report['artifacts'] = {'screenshots': [], 'dom_snapshots': [], 'network_logs': {}}

            # Add to artifacts.screenshots ONLY
            report['artifacts']['screenshots'].append({
                'name': 'baseline',
                'path': baseline_screenshot_path,
                'timestamp': datetime.now().isoformat()
            })

        # Capture baseline data
        report['baseline'] = self._capture_complete_baseline()
        report['baseline']['screenshot'] = baseline_screenshot_path if baseline_screenshot else None

        # PHASE 1: Basic reconnaissance (always do this)
        self.logger.info("PHASE 1: Basic reconnaissance...")
        report['discovered_features'] = self._catalog_site_features()
        report['downloadable_content'] = self._find_downloadables()
        report['access_barriers'] = self._detect_barriers()

        # ADD: Form discovery (critical for scrapers!)
        report['forms'] = self._discover_all_forms()

        # ADD: Initial AJAX patterns
        report['ajax_patterns'] = self.toolkit.detect_ajax_patterns(self.driver, wait_time=3)

        self._capture_checkpoint("after_phase1", report)  # Pass report!

        # PHASE 2: Liberation tactics
        if not safe_mode:
            self.logger.info("LIBERATION MODE: Deploying tactics...")
            report['liberation_results'] = self._run_liberation_tactics()
        else:
            self.logger.info("️SAFE MODE: Using only non-invasive tactics...")
            report['liberation_results'] = self._run_safe_tactics()

        self._capture_checkpoint("after_liberation", report)  # Pass report!

        # PHASE 3: Deep analysis FOR SCRAPER BUILDING
        self.logger.info("PHASE 3: Deep scraper-focused analysis...")

        # Core discoveries
        report['search_patterns'] = self._discover_search_patterns()
        report['pagination_patterns'] = self._discover_pagination_patterns()
        report['data_structures'] = self._analyze_data_structures()
        report['tech_stack'] = self._detect_technology_stack()

        # ADD: Critical for scraper building!
        report['navigation_flows'] = self._map_navigation_flows()
        report['download_mechanisms'] = self._test_download_methods()
        report['authentication_flow'] = self._probe_authentication()
        report['rate_limits'] = self._detect_rate_limits()
        report['url_patterns'] = self._analyze_url_structures()

        self._capture_checkpoint("after_analysis", report)  # Pass report!

        # PHASE 4: Task-specific exploration
        if hasattr(self, 'current_task') and self.current_task:
            self.logger.info("PHASE 4: Task-specific exploration...")
            report['task_discoveries'] = self._execute_task_exploration(self.current_task)
            self._capture_checkpoint("after_task_exploration", report)  # Pass report!

        # PHASE 5: Network analysis summary
        self.logger.info("PHASE 5: Network pattern analysis...")
        report['network_summary'] = self._analyze_captured_network()

        # Compile all captured data
        report['captured_data'] = self.captured_data

        # PHASE 6: Generate scraper blueprint
        report['scraper_blueprint'] = self._generate_scraper_blueprint(report)
        report['recommended_approach'] = self._generate_recommendations(report)

        # REMOVED: _consolidate_screenshots() - no longer needed!

        # Final capture
        self._capture_checkpoint("final_state", report)  # Pass report!

        # Save comprehensive report
        self._save_comprehensive_report(report)

        return report

    def execute_with_task(self, url: str, task: Dict, safe_mode: bool = False) -> Dict:
        """Execute recon with task-specific exploration"""
        self.current_task = task
        report = self.scout_site(url, safe_mode)

        # Handle scout_site failure
        if not report:
            self.logger.error(f"Scout site failed for {url}")
            return {
                'error': 'Scout site failed',
                'url': url,
                'task': task,
                'timestamp': datetime.now().isoformat()
            }

        # Task-specific comparison (not validation - just data!)
        if task.get('expected_features'):
            report['expectation_comparison'] = self._compare_findings_to_expectations(
                report,
                task.get('expected_features', {})
            )

        return report

    def _run_safe_tactics(self, report: Dict) -> List[Dict]:
        """Run only gentle tactics - PRODUCTION READY"""
        results = []
        toolkit = self.toolkit

        # Define safe tactics
        safe_tactics = [
            {
                'name': 'remove_overlays',
                'description': 'Remove popups and overlays blocking content',
                'method': lambda: toolkit.remove_overlays(self.driver, screenshot_after=True)
            },
            {
                'name': 'expand_content',
                'description': 'Expand collapsed sections and hidden content',
                'method': lambda: toolkit.expand_collapsed_content(self.driver)
            },
            {
                'name': 'extract_hidden_data',
                'description': 'Extract metadata and hidden information',
                'method': lambda: toolkit.extract_hidden_data(self.driver)
            },
            {
                'name': 'detect_ajax',
                'description': 'Monitor AJAX/dynamic content patterns',
                'method': lambda: toolkit.detect_ajax_patterns(self.driver, wait_time=3)
            },
            {
                'name': 'disable_lazy_loading',
                'description': 'Force lazy-loaded content to appear',
                'method': lambda: toolkit.disable_lazy_loading(self.driver)
            },
            {
                'name': 'extract_shadow_dom',
                'description': 'Extract content from shadow DOM elements',
                'method': lambda: toolkit.extract_shadow_dom(self.driver)
            }
        ]

        # Execute each safe tactic
        for tactic in safe_tactics:
            self.logger.info(f"[SAFE] Executing: {tactic['name']}")

            try:
                # Capture state before tactic
                before_state = {
                    'url': self.driver.current_url,
                    'element_count': len(self.driver.find_elements(By.XPATH, '//*')),
                    'timestamp': datetime.now().isoformat()
                }

                # Execute the tactic
                start_time = time.time()
                result = tactic['method']()
                execution_time = time.time() - start_time

                # Build enhanced result
                enhanced_result = {
                    'tactic': tactic['name'],
                    'description': tactic['description'],
                    'executed_at': before_state['timestamp'],
                    'execution_time': execution_time,
                    'success': result.get('success', False),
                    'details': result.get('details', ''),
                    'data': result.get('data', {}) if result.get('success') else {},
                    'error': result.get('error', None),
                    'impact': self._measure_tactic_impact(before_state)
                }

                # Handle success
                if enhanced_result['success']:
                    self.logger.info(f"[SAFE] Success: {tactic['name']} - {enhanced_result['details']}")

                    # Take screenshot if something changed
                    if enhanced_result['impact']['elements_changed'] > 0:
                        try:
                            screenshot = self.take_screenshot(f"safe_{tactic['name']}")
                            if screenshot:
                                screenshot_path = str(screenshot.absolute())
                                enhanced_result['screenshot'] = screenshot_path

                                # CRITICAL: Add to report artifacts!
                                report['artifacts']['screenshots'].append({
                                    'name': f"safe_{tactic['name']}",
                                    'path': screenshot_path,
                                    'timestamp': enhanced_result['executed_at']
                                })
                                self.logger.debug(f"Screenshot added to artifacts: safe_{tactic['name']}")
                        except Exception as e:
                            self.logger.warning(f"Screenshot failed for {tactic['name']}: {e}")
                else:
                    self.logger.warning(f"[SAFE] Failed: {tactic['name']} - {enhanced_result.get('error', 'Unknown')}")

                results.append(enhanced_result)

                # Brief pause between tactics
                time.sleep(0.5)

            except Exception as e:
                self.logger.error(f"[SAFE] Exception in {tactic['name']}: {e}")
                results.append({
                    'tactic': tactic['name'],
                    'description': tactic['description'],
                    'executed_at': datetime.now().isoformat(),
                    'execution_time': 0,
                    'success': False,
                    'error': str(e),
                    'details': f'Exception: {type(e).__name__}'
                })

        # Summary
        successful_count = sum(1 for r in results if r['success'])
        self.logger.info(f"[SAFE] Completed {successful_count}/{len(results)} tactics successfully")

        return results

    def _run_liberation_tactics(self, report: Dict) -> List[Dict]:
        """Run ALL tactics from toolkit - PRODUCTION READY"""
        results = []
        toolkit = self.toolkit

        # Full liberation sequence - ordered by increasing invasiveness
        liberation_sequence = [
            # LEVEL 1: Visibility Enhancement (Safe)
            {
                'name': 'remove_overlays',
                'level': 1,
                'description': 'Remove modal overlays and popups',
                'method': lambda: toolkit.remove_overlays(self.driver, screenshot_after=True)
            },
            {
                'name': 'expand_content',
                'level': 1,
                'description': 'Expand all collapsed content',
                'method': lambda: toolkit.expand_collapsed_content(self.driver)
            },
            {
                'name': 'remove_sticky',
                'level': 1,
                'description': 'Remove sticky headers/footers',
                'method': lambda: toolkit.remove_sticky_elements(self.driver)
            },
            {
                'name': 'reveal_hidden',
                'level': 1,
                'description': 'Make hidden elements visible',
                'method': lambda: toolkit.reveal_hidden_elements(self.driver)
            },
            {
                'name': 'disable_lazy_loading',
                'level': 1,
                'description': 'Force lazy-loaded content to appear',
                'method': lambda: toolkit.disable_lazy_loading(self.driver)
            },

            # LEVEL 2: Access Enhancement
            {
                'name': 'bypass_right_click',
                'level': 2,
                'description': 'Enable right-click and text selection',
                'method': lambda: toolkit.bypass_right_click_protection(self.driver)
            },
            {
                'name': 'bypass_paywall',
                'level': 2,
                'description': 'Attempt paywall bypass techniques',
                'method': lambda: toolkit.bypass_paywall(self.driver)
            },

            # LEVEL 3: Authentication & Cookies
            {
                'name': 'manipulate_cookies',
                'level': 3,
                'description': 'Set authentication cookies',
                'method': lambda: toolkit.manipulate_cookies(self.driver)
            },
            {
                'name': 'override_js_checks',
                'level': 3,
                'description': 'Override JavaScript authentication checks',
                'method': lambda: toolkit.override_javascript_checks(self.driver)
            },
            {
                'name': 'spoof_referrer',
                'level': 3,
                'description': 'Spoof referrer to appear from search',
                'method': lambda: toolkit.spoof_referrer(self.driver)
            },

            # LEVEL 4: Data Extraction
            {
                'name': 'extract_hidden_data',
                'level': 4,
                'description': 'Extract all hidden metadata',
                'method': lambda: toolkit.extract_hidden_data(self.driver)
            },
            {
                'name': 'extract_shadow_dom',
                'level': 4,
                'description': 'Extract shadow DOM content',
                'method': lambda: toolkit.extract_shadow_dom(self.driver)
            },
            {
                'name': 'extract_storage',
                'level': 4,
                'description': 'Extract browser storage data',
                'method': lambda: toolkit.extract_browser_storage(self.driver)
            },
            {
                'name': 'extract_canvas',
                'level': 4,
                'description': 'Extract canvas/chart data',
                'method': lambda: toolkit.extract_canvas_data(self.driver)
            },

            # LEVEL 5: Network Analysis
            {
                'name': 'detect_ajax',
                'level': 5,
                'description': 'Deep AJAX pattern detection',
                'method': lambda: toolkit.detect_ajax_patterns(self.driver, wait_time=5)
            },
            {
                'name': 'intercept_downloads',
                'level': 5,
                'description': 'Intercept download attempts',
                'method': lambda: toolkit.intercept_downloads(self.driver)
            },

            # LEVEL 6: Advanced Tactics
            {
                'name': 'humanize_browser',
                'level': 6,
                'description': 'Make browser appear human-controlled',
                'method': lambda: toolkit.humanize_browser(self.driver)
            },
            {
                'name': 'probe_endpoints',
                'level': 6,
                'description': 'Probe for hidden API endpoints',
                'method': lambda: toolkit.probe_endpoints(self.driver, self.driver.current_url)
            },
            {
                'name': 'bypass_cloudflare',
                'level': 6,
                'description': 'Attempt Cloudflare bypass',
                'method': lambda: toolkit.bypass_cloudflare(self.driver)
            }
        ]

        # Track which levels we've executed
        levels_executed = set()

        # Execute tactics by level
        for tactic in liberation_sequence:
            level = tactic['level']

            # Log level transition
            if level not in levels_executed:
                self.logger.info(f"[LIBERATION] Entering Level {level} tactics")
                levels_executed.add(level)
                time.sleep(1)  # Pause between levels

            self.logger.info(f"[LIBERATION] Executing: {tactic['name']} (Level {level})")

            try:
                # Capture before state
                before_state = self._capture_state_snapshot()

                # Execute tactic with timeout protection
                start_time = time.time()
                result = tactic['method']()
                execution_time = time.time() - start_time

                # Capture after state
                after_state = self._capture_state_snapshot()

                # Build comprehensive result
                enhanced_result = {
                    'tactic': tactic['name'],
                    'level': level,
                    'description': tactic['description'],
                    'executed_at': datetime.now().isoformat(),
                    'execution_time': execution_time,
                    'success': result.get('success', False),
                    'details': result.get('details', ''),
                    'data': result.get('data', {}) if result.get('success') else {},
                    'error': result.get('error', None),
                    'impact': self._calculate_impact(before_state, after_state),
                    'state_changes': self._detect_state_changes(before_state, after_state)
                }

                # Handle success
                if enhanced_result['success']:
                    self.logger.info(f"[LIBERATION] SUCCESS: {tactic['name']} - {enhanced_result['details']}")

                    # Screenshot if significant changes
                    if enhanced_result['impact']['significant_change']:
                        try:
                            screenshot = self.take_screenshot(f"liberation_{tactic['name']}")
                            if screenshot:
                                screenshot_path = str(screenshot.absolute())
                                enhanced_result['screenshot'] = screenshot_path

                                # CRITICAL: Add to report artifacts!
                                report['artifacts']['screenshots'].append({
                                    'name': f"liberation_{tactic['name']}",
                                    'path': screenshot_path,
                                    'timestamp': enhanced_result['executed_at']
                                })
                                self.logger.debug(f"Screenshot added to artifacts: liberation_{tactic['name']}")
                        except Exception as e:
                            self.logger.warning(f"Screenshot failed for {tactic['name']}: {e}")
                else:
                    self.logger.warning(
                        f"[LIBERATION] FAILED: {tactic['name']} - {enhanced_result.get('error', 'Unknown')}")

                results.append(enhanced_result)

                # Adaptive timing based on level
                if level <= 2:
                    time.sleep(0.5)  # Quick pause for safe tactics
                elif level <= 4:
                    time.sleep(1)  # Medium pause for invasive tactics
                else:
                    time.sleep(2)  # Longer pause for advanced tactics

            except Exception as e:
                self.logger.error(f"[LIBERATION] Exception in {tactic['name']}: {e}")
                results.append({
                    'tactic': tactic['name'],
                    'level': level,
                    'description': tactic['description'],
                    'executed_at': datetime.now().isoformat(),
                    'execution_time': 0,
                    'success': False,
                    'error': str(e),
                    'details': f'Exception: {type(e).__name__}'
                })

        # Summary
        successful = sum(1 for r in results if r['success'])
        by_level = {}
        for r in results:
            level = r['level']
            if level not in by_level:
                by_level[level] = {'total': 0, 'successful': 0}
            by_level[level]['total'] += 1
            if r['success']:
                by_level[level]['successful'] += 1

        self.logger.info(f"[LIBERATION] Completed {successful}/{len(results)} tactics successfully")
        for level, stats in sorted(by_level.items()):
            self.logger.info(f"[LIBERATION] Level {level}: {stats['successful']}/{stats['total']} successful")

        return results

    # ////

    def _capture_complete_baseline(self) -> Dict:
        """Capture EVERYTHING about the initial page state"""
        baseline = {
            'timestamp': datetime.now().isoformat(),
            'url': self.driver.current_url,
            'title': self.driver.title,
            'ready_state': 'unknown',
            # REMOVED 'screenshot' - handled in scout_site()
            'dom': {},
            'metadata': {},
            'js_environment': {},
            'metrics': {},
            'raw_html': '',
            'html_file': None,
            'viewport': {},
            'cookies': []
        }

        try:
            # 1. Capture ready state
            baseline['ready_state'] = self.driver.execute_script("return document.readyState")

            # 2. REMOVED duplicate screenshot logic

            # 3. Capture complete DOM structure
            baseline['dom'] = self._capture_full_dom()

            # 4. Extract all metadata
            baseline['metadata'] = self._extract_all_metadata()

            # 5. Capture JavaScript environment
            baseline['js_environment'] = self._capture_js_environment()

            # 6. Capture page metrics
            baseline['metrics'] = self._capture_page_metrics()

            # 7. Get raw HTML
            baseline['raw_html'] = self.driver.page_source

            # 8. Save HTML to file for reference
            html_path = self.base_path / 'html_snapshots'
            html_path.mkdir(exist_ok=True)

            html_file = html_path / f"baseline_{int(time.time())}.html"
            html_file.write_text(baseline['raw_html'], encoding='utf-8')
            baseline['html_file'] = str(html_file.absolute())  # Use absolute path

            # 9. Capture viewport information
            baseline['viewport'] = self.driver.execute_script("""
                return {
                    width: window.innerWidth,
                    height: window.innerHeight,
                    devicePixelRatio: window.devicePixelRatio,
                    orientation: screen.orientation ? screen.orientation.type : 'unknown'
                };
            """)

            # 10. Capture initial cookies
            baseline['cookies'] = self.driver.get_cookies()

            # 11. Capture monitoring data if available
            try:
                monitoring_data = self.driver.execute_script("return window.__reconMonitoring || {};")
                if monitoring_data:
                    baseline['monitoring_snapshot'] = {
                        'network_requests': len(monitoring_data.get('network', [])),
                        'console_logs': len(monitoring_data.get('console', [])),
                        'errors': len(monitoring_data.get('errors', [])),
                        'dom_mutations': len(monitoring_data.get('domMutations', []))
                    }
            except Exception as e:
                self.logger.debug(f"Monitoring data not available: {e}")

            self.logger.info("[BASELINE] Complete baseline captured")

        except Exception as e:
            self.logger.error(f"[BASELINE] Error capturing baseline: {e}")
            baseline['capture_error'] = str(e)

        return baseline

    def _capture_checkpoint(self, checkpoint_name: str, report: Dict):
        """Capture comprehensive state at specific checkpoints - FIXED"""
        checkpoint_data = {
            'name': checkpoint_name,
            'timestamp': datetime.now().isoformat(),
            'url': self.driver.current_url,
            'title': self.driver.title,
            'ready_state': self.driver.execute_script("return document.readyState"),
            'dom_changes': self._detect_dom_changes(),
            'new_elements': self._find_new_elements(),
            'network_activity': self._get_recent_network(),
            'metrics': self._capture_current_metrics()
        }

        # Take screenshot and add to report artifacts
        try:
            screenshot_path = self.take_screenshot(f"checkpoint_{checkpoint_name}")
            if screenshot_path:
                screenshot_abs_path = str(screenshot_path.absolute())

                # Add to report artifacts.screenshots
                if 'artifacts' not in report:
                    report['artifacts'] = {'screenshots': [], 'dom_snapshots': [], 'network_logs': {}}

                report['artifacts']['screenshots'].append({
                    'name': f"checkpoint_{checkpoint_name}",
                    'path': screenshot_abs_path,
                    'timestamp': checkpoint_data['timestamp']
                })

                # Reference in checkpoint data
                checkpoint_data['screenshot'] = screenshot_abs_path

        except Exception as e:
            self.logger.warning(f"Screenshot failed at checkpoint {checkpoint_name}: {e}")

        # Store checkpoint data
        self.captured_data['dom_snapshots'].append(checkpoint_data)
        self.captured_data['metadata_timeline'].append({
            'checkpoint': checkpoint_name,
            'timestamp': checkpoint_data['timestamp'],
            'event': f"Captured checkpoint: {checkpoint_name}"
        })

        self.logger.info(f"[CHECKPOINT] Captured: {checkpoint_name}")

    def _capture_full_dom(self) -> Dict:
        """Capture complete DOM structure and content"""
        dom_script = """
        function captureDom(element = document.documentElement) {
            const node = {
                tag: element.tagName,
                attributes: {},
                children: [],
                text: '',
                computed_style: {}
            };

            // Capture attributes
            for (let attr of element.attributes || []) {
                node.attributes[attr.name] = attr.value;
            }

            // Capture important computed styles
            if (element.tagName) {
                const style = window.getComputedStyle(element);
                node.computed_style = {
                    display: style.display,
                    visibility: style.visibility,
                    position: style.position,
                    zIndex: style.zIndex
                };
            }

            // Capture children
            for (let child of element.children || []) {
                node.children.push(captureDom(child));
            }

            // Capture text
            if (element.childNodes.length === 1 && element.childNodes[0].nodeType === 3) {
                node.text = element.textContent.trim();
            }

            return node;
        }

        return {
            structure: captureDom(),
            total_elements: document.querySelectorAll('*').length,
            interactive_elements: document.querySelectorAll('button, a, input, select, textarea').length,
            forms: document.forms.length,
            images: document.images.length,
            scripts: document.scripts.length
        };
        """

        return self.driver.execute_script(dom_script)

    def _capture_js_environment(self) -> Dict:
        """Capture JavaScript environment details"""
        js_env_script = """
        const env = {
            // Global variables (non-standard)
            custom_globals: [],
            // Detected frameworks
            frameworks: {},
            // Available APIs
            apis: {},
            // Custom events
            custom_events: []
        };

        // Find custom globals
        const standardGlobals = ['window', 'document', 'console', 'navigator', 'location'];
        for (let key in window) {
            if (!standardGlobals.includes(key) && !key.startsWith('webkit') && !key.startsWith('moz')) {
                try {
                    const type = typeof window[key];
                    if (type !== 'function' || key.charAt(0) === key.charAt(0).toUpperCase()) {
                        env.custom_globals.push({
                            name: key,
                            type: type,
                            sample: type === 'object' ? Object.keys(window[key] || {}).slice(0, 5) : String(window[key]).substring(0, 100)
                        });
                    }
                } catch(e) {
                    // Add to a list of problematic globals
                    env.error_globals = env.error_globals || [];
                    env.error_globals.push(key);
                }
            }
        }

        // Detect frameworks
        env.frameworks = {
            jquery: typeof jQuery !== 'undefined' ? jQuery.fn.jquery : false,
            react: typeof React !== 'undefined',
            angular: typeof angular !== 'undefined',
            vue: typeof Vue !== 'undefined',
            bootstrap: typeof bootstrap !== 'undefined'
        };

        // Available APIs
        env.apis = {
            fetch: typeof fetch !== 'undefined',
            websocket: typeof WebSocket !== 'undefined',
            indexeddb: typeof indexedDB !== 'undefined',
            serviceworker: 'serviceWorker' in navigator
        };

        return env;
        """

        return self.driver.execute_script(js_env_script)

    def _capture_page_metrics(self) -> Dict:
        """Capture page performance and size metrics"""
        metrics_script = """
        const perf = performance.timing;
        const metrics = {
            // Page load timing
            timing: {
                total_load_time: perf.loadEventEnd - perf.navigationStart,
                dom_content_loaded: perf.domContentLoadedEventEnd - perf.navigationStart,
                dom_interactive: perf.domInteractive - perf.navigationStart
            },
            // Resource counts
            resources: {
                images: document.images.length,
                scripts: document.scripts.length,
                stylesheets: document.styleSheets.length,
                iframes: document.querySelectorAll('iframe').length,
                total_elements: document.querySelectorAll('*').length
            },
            // Memory (if available)
            memory: performance.memory ? {
                used: Math.round(performance.memory.usedJSHeapSize / 1048576) + ' MB',
                total: Math.round(performance.memory.totalJSHeapSize / 1048576) + ' MB'
            } : null
        };

        return metrics;
        """

        return self.driver.execute_script(metrics_script)

    def _capture_state_snapshot(self) -> Dict:
        """Capture current page state for comparison"""
        try:
            return {
                'url': self.driver.current_url,
                'title': self.driver.title,
                'element_count': len(self.driver.find_elements(By.XPATH, '//*')),
                'body_length': len(self.driver.find_element(By.TAG_NAME, 'body').text),
                'cookies': len(self.driver.get_cookies()),
                'local_storage_items': self.driver.execute_script('return Object.keys(localStorage).length'),
                'timestamp': time.time()
            }
        except Exception as e:
            self.logger.debug(f"State snapshot error: {e}")
            return {
                'timestamp': time.time(),
                'error': str(e)
            }

    def _capture_current_metrics(self) -> Dict[str, Any]:
        """Capture current page performance metrics"""
        metrics = {}

        try:
            metrics = self.driver.execute_script("""
                const perf = performance.timing;
                const now = Date.now();

                return {
                    // Page load metrics
                    dom_ready: perf.domContentLoadedEventEnd - perf.navigationStart,
                    load_complete: perf.loadEventEnd - perf.navigationStart,

                    // Resource metrics
                    resource_count: performance.getEntriesByType('resource').length,

                    // Memory (if available)
                    memory_used: performance.memory ? 
                        Math.round(performance.memory.usedJSHeapSize / 1048576) : null,

                    // Current state
                    ready_state: document.readyState,
                    visibility: document.visibilityState,

                    // Interaction metrics
                    clickable_elements: document.querySelectorAll('button, a[href], [onclick]').length,
                    form_count: document.forms.length,
                    input_count: document.querySelectorAll('input, select, textarea').length
                };
            """)
        except Exception as e:
            self.logger.debug(f"Metrics capture error: {e}")
            metrics['error'] = str(e)
        return metrics

    # ////

    def _discover_all_forms(self) -> Dict:
        """Find ALL forms and their submission patterns"""
        try:
            forms_script = """
            const forms = [];
            document.querySelectorAll('form').forEach((form, index) => {
                const formData = {
                    index: index,
                    action: form.action,
                    method: form.method,
                    id: form.id,
                    classes: form.className,
                    enctype: form.enctype,  // ADD: Important for file uploads
                    target: form.target,     // ADD: New window submissions
                    inputs: [],
                    hidden_inputs: [],       // ADD: Track separately
                    buttons: [],
                    purpose: null            // ADD: Will detect below
                };

                // Detect form purpose
                const actionLower = (form.action || '').toLowerCase();
                const idLower = (form.id || '').toLowerCase();
                if (actionLower.includes('login') || idLower.includes('login')) {
                    formData.purpose = 'login';
                } else if (actionLower.includes('search') || idLower.includes('search')) {
                    formData.purpose = 'search';
                } else if (actionLower.includes('contact') || idLower.includes('contact')) {
                    formData.purpose = 'contact';
                }

                // Get all inputs
                form.querySelectorAll('input, select, textarea').forEach(input => {
                    const inputData = {
                        type: input.type,
                        name: input.name,
                        id: input.id,
                        required: input.required,
                        placeholder: input.placeholder
                        // REMOVED: value - security risk!
                    };

                    if (input.type === 'hidden') {
                        formData.hidden_inputs.push(inputData);
                    } else {
                        formData.inputs.push(inputData);
                    }
                });

                // Get submit buttons
                form.querySelectorAll('button, input[type="submit"]').forEach(btn => {
                    formData.buttons.push({
                        text: btn.textContent.trim(),  // ADD: trim()
                        type: btn.type || 'submit',    // ADD: default
                        // REMOVED: onclick - security risk, not needed
                    });
                });

                forms.push(formData);
            });
            return forms;
            """
            return self.driver.execute_script(forms_script)
        except Exception as e:
            self.logger.debug(f"Form discovery error: {e}")
            return []  # Return empty list on error

    def _discover_search_patterns(self) -> Dict[str, Any]:
        """Discover how search works on this site"""
        search_patterns = {
            'has_search': False,
            'search_methods': [],
            'search_endpoints': [],
            'search_parameters': {},
            'search_type': None,  # 'form', 'ajax', 'url_based', 'instant'
            'has_instant_search': False,  # ADD: New field
            'autocomplete_endpoints': []  # ADD: For instant search
        }

        try:
            # Find search elements
            search_data = self.driver.execute_script("""
                const search = {
                    forms: [],
                    inputs: [],
                    endpoints: [],
                    instant_search: false,
                    autocomplete: []
                };

                // Find search forms
                document.querySelectorAll('form').forEach(form => {
                    const action = form.action || '';
                    const hasSearchInput = form.querySelector(
                        'input[type="search"], input[name*="search"], input[name*="query"], input[name="q"]'
                    );

                    if (hasSearchInput || action.includes('search')) {
                        search.forms.push({
                            action: action,
                            method: form.method || 'GET',
                            id: form.id || null,
                            inputs: Array.from(form.querySelectorAll('input')).map(i => ({
                                name: i.name,
                                type: i.type,
                                placeholder: i.placeholder
                            }))
                        });
                    }
                });

                // Find standalone search inputs
                document.querySelectorAll(
                    'input[type="search"], input[placeholder*="search" i], input[name*="search" i]'
                ).forEach(input => {
                    if (!input.form) {  // Not part of a form
                        search.inputs.push({
                            name: input.name,
                            id: input.id,
                            placeholder: input.placeholder,
                            classes: input.className
                        });

                        // Check for instant search indicators
                        if (input.hasAttribute('data-instant') || 
                            input.hasAttribute('data-autocomplete') ||
                            input.classList.contains('instant-search') ||
                            input.getAttribute('autocomplete') === 'on') {
                            search.instant_search = true;
                        }
                    }
                });

                // Look for search in links - WITH SAFETY
                document.querySelectorAll('a[href*="search"], a[href*="?q="]').forEach(link => {
                    try {  // ADD: Safety wrapper
                        const url = new URL(link.href);
                        if (url.search) {
                            search.endpoints.push({
                                url: url.pathname,
                                params: Object.fromEntries(url.searchParams)
                            });
                        }
                    } catch(e) {
                        // Invalid URL, skip silently
                    }
                });

                // ADD: Look for autocomplete/typeahead endpoints
                const scripts = Array.from(document.scripts);
                scripts.forEach(script => {
                    const content = script.textContent || '';
                    // Common patterns for autocomplete endpoints
                    const patterns = [
                        /autocomplete['"]\s*:\s*['"]([^'"]+)['"]/,
                        /typeahead['"]\s*:\s*['"]([^'"]+)['"]/,
                        /suggest['"]\s*:\s*['"]([^'"]+)['"]/,
                        /search.*url['"]\s*:\s*['"]([^'"]+)['"]/i
                    ];

                    patterns.forEach(pattern => {
                        const match = content.match(pattern);
                        if (match && match[1]) {
                            search.autocomplete.push(match[1]);
                        }
                    });
                });

                return search;
            """)

            # Process results
            if search_data['forms'] or search_data['inputs']:
                search_patterns['has_search'] = True

            # Determine search type
            if search_data['forms']:
                search_patterns['search_type'] = 'form'
                search_patterns['search_methods'] = [f['method'] for f in search_data['forms']]

                # Extract parameters
                for form in search_data['forms']:
                    for input_field in form.get('inputs', []):
                        if input_field['name']:
                            search_patterns['search_parameters'][input_field['name']] = input_field['type']

            elif search_data['inputs']:
                search_patterns['search_type'] = 'ajax'  # Likely AJAX if no form

            # Extract endpoints
            for endpoint in search_data.get('endpoints', []):
                search_patterns['search_endpoints'].append(endpoint['url'])

            # ADD: Process instant search findings
            if search_data.get('instant_search'):
                search_patterns['has_instant_search'] = True
                if search_patterns['search_type'] == 'form':
                    search_patterns['search_type'] = 'instant'  # Upgrade type

            # ADD: Store autocomplete endpoints
            search_patterns['autocomplete_endpoints'] = search_data.get('autocomplete', [])

        except Exception as e:
            self.logger.debug(f"Search pattern discovery error: {e}")

        return search_patterns

    def _discover_pagination_patterns(self) -> Dict[str, Any]:
        """Discover pagination patterns"""
        pagination = {
            'has_pagination': False,
            'style': None,  # 'numbered', 'load_more', 'infinite', 'next_prev'
            'selectors': [],
            'url_patterns': [],  # Changed to array
            'total_pages': None,
            'current_page': None
        }

        try:
            pagination_data = self.driver.execute_script("""
                const pagination = {
                    style: null,
                    selectors: [],
                    patterns: [],
                    current: null,
                    total: null
                };

                // Check for numbered pagination
                const numbered = document.querySelector(
                    '.pagination, .pager, nav[aria-label*="pagination"], [class*="page-numbers"]'
                );
                if (numbered) {
                    pagination.style = 'numbered';
                    pagination.selectors.push({
                        type: 'container',
                        selector: numbered.tagName + '.' + numbered.className
                    });

                    // Try to find current/total pages
                    const current = numbered.querySelector('.current, .active, [aria-current="page"]');
                    if (current) pagination.current = current.textContent.trim();

                    const pages = numbered.querySelectorAll('a[href*="page"]');
                    if (pages.length > 0) {
                        pagination.total = pages[pages.length - 1].textContent.trim();
                    }
                }

                // Check for load more button
                const loadMore = Array.from(document.querySelectorAll('button, a')).find(el => 
                    el.textContent.toLowerCase().includes('load more') ||
                    el.textContent.toLowerCase().includes('show more') ||
                    el.textContent.toLowerCase().includes('view more')
                );
                if (loadMore) {
                    pagination.style = pagination.style || 'load_more';
                    pagination.selectors.push({
                        type: 'load_more',
                        selector: loadMore.tagName + 
                                 (loadMore.id ? '#' + loadMore.id : '') + 
                                 (loadMore.className ? '.' + loadMore.className.split(' ')[0] : '')
                    });
                }

                // Check for next/prev only
                const hasNext = document.querySelector('a[rel="next"], .next-page, [aria-label*="next"]');
                const hasPrev = document.querySelector('a[rel="prev"], .prev-page, [aria-label*="previous"]');
                if (hasNext || hasPrev) {
                    pagination.style = pagination.style || 'next_prev';
                }

                // Extract URL patterns
                document.querySelectorAll('a[href*="page"], a[href*="p="], a[href*="offset"]').forEach(link => {
                    try {
                        const url = new URL(link.href);
                        const pattern = url.pathname + url.search.replace(/\\d+/g, '{n}');
                        if (!pagination.patterns.includes(pattern)) {
                            pagination.patterns.push(pattern);
                        }
                    } catch(e) {}
                });

                return pagination;
            """)

            # Safely merge results without overwriting structure
            if pagination_data:
                pagination['has_pagination'] = bool(pagination_data.get('style'))
                pagination['style'] = pagination_data.get('style')
                pagination['selectors'] = pagination_data.get('selectors', [])
                pagination['url_patterns'] = pagination_data.get('patterns', [])
                pagination['current_page'] = pagination_data.get('current')
                pagination['total_pages'] = pagination_data.get('total')

        except Exception as e:
            self.logger.debug(f"Pagination discovery error: {e}")

        return pagination

    # ////

    def _find_downloadables(self) -> List[Dict]:
        """Find all downloadable content on the page"""
        downloadables = []

        try:
            # JavaScript to find all potential downloads
            download_data = self.driver.execute_script("""
                const downloads = [];

                // Comprehensive download extensions
                const downloadExtensions = [
                    // Documents
                    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.csv', '.txt', '.rtf', '.odt',
                    // Archives
                    '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2',
                    // Data
                    '.json', '.xml', '.sql', '.db',
                    // Presentations
                    '.ppt', '.pptx', '.odp',
                    // Media (sometimes downloadable)
                    '.mp3', '.mp4', '.wav', '.avi', '.mov', '.mkv',
                    // Other
                    '.epub', '.mobi', '.ics', '.vcf'
                ];

                // Helper to extract extension safely
                function getExtension(url) {
                    try {
                        const urlObj = new URL(url);
                        const pathname = urlObj.pathname;
                        const match = pathname.match(/\\.([a-zA-Z0-9]+)$/);
                        return match ? match[1].toLowerCase() : null;
                    } catch(e) {
                        return null;
                    }
                }

                // Find links with download extensions
                document.querySelectorAll('a[href]').forEach(link => {
                    try {
                        const href = link.href;
                        const extension = getExtension(href);
                        const hasDownloadAttr = link.hasAttribute('download');
                        const hasDownloadExt = extension && downloadExtensions.some(ext => ext.slice(1) === extension);

                        if (hasDownloadAttr || hasDownloadExt) {
                            downloads.push({
                                type: 'direct_download',
                                url: href,
                                text: link.textContent.trim().substring(0, 100),
                                filename: link.download || link.pathname.split('/').pop() || 'unknown',
                                extension: extension || 'unknown',
                                size_hint: link.title && link.title.match(/\\d+\\s*(KB|MB|GB)/i) ? 
                                           link.title.match(/\\d+\\s*(KB|MB|GB)/i)[0] : null
                            });
                        }
                    } catch(e) {
                        // Skip invalid links
                    }
                });

                // Buttons that might trigger downloads - ENHANCED
                document.querySelectorAll('button, [role="button"], a.button, a.btn').forEach(button => {
                    const text = button.textContent.toLowerCase();
                    const downloadKeywords = [
                        'download', 'export', 'save', 'pdf', 'csv', 'excel', 
                        'print', 'generate', 'report', 'backup', 'extract'
                    ];

                    if (downloadKeywords.some(keyword => text.includes(keyword))) {
                        const buttonInfo = {
                            type: 'button_download',
                            text: button.textContent.trim(),
                            id: button.id || null,
                            classes: button.className || null,
                            data_attributes: {}
                        };

                        // Capture data attributes that might have download info
                        for (let attr of button.attributes) {
                            if (attr.name.startsWith('data-')) {
                                buttonInfo.data_attributes[attr.name] = attr.value;
                            }
                        }

                        downloads.push(buttonInfo);
                    }
                });

                // Forms that might generate downloads
                document.querySelectorAll('form').forEach(form => {
                    const action = form.action || '';
                    const formClasses = form.className || '';

                    if (action.match(/export|download|report|generate/i) || 
                        formClasses.match(/export|download|report/i)) {
                        downloads.push({
                            type: 'form_download',
                            action: action,
                            method: form.method || 'GET',
                            id: form.id || null,
                            name: form.name || null
                        });
                    }
                });

                // iframes that might contain documents
                document.querySelectorAll('iframe').forEach(iframe => {
                    if (iframe.src) {
                        const extension = getExtension(iframe.src);
                        if (extension && downloadExtensions.some(ext => ext.slice(1) === extension)) {
                            downloads.push({
                                type: 'iframe_document',
                                url: iframe.src,
                                title: iframe.title || iframe.name || 'Embedded Document',
                                extension: extension
                            });
                        }
                    }
                });

                return downloads;
            """)

            # Process the results
            for item in download_data:
                # Add metadata
                item['discovered_at'] = datetime.now().isoformat()
                item['page_url'] = self.driver.current_url
                downloadables.append(item)

            self.logger.info(f"[DISCOVERY] Found {len(downloadables)} downloadable items")

        except Exception as e:
            self.logger.debug(f"Downloadables discovery error: {e}")

        return downloadables

    def _find_query_parameters(self) -> Dict[str, Dict[str, Any]]:
        """Find and analyze query parameters used in URLs"""
        params = {}

        try:
            param_data = self.driver.execute_script("""
                const params = {};

                document.querySelectorAll('a[href*="?"]').forEach(a => {
                    try {  // ADD: Safety wrapper
                        const url = new URL(a.href);

                        url.searchParams.forEach((value, key) => {
                            if (!params[key]) {
                                params[key] = {
                                    values: new Set(),
                                    examples: [],
                                    type: null,
                                    count: 0
                                };
                            }

                            // Store unique values (no arbitrary limit)
                            params[key].values.add(value);
                            params[key].count++;

                            // Keep a few examples with context
                            if (params[key].examples.length < 3) {
                                params[key].examples.push({
                                    value: value,
                                    link_text: a.textContent.trim().substring(0, 50),
                                    full_url: url.href
                                });
                            }

                            // Detect parameter type
                            if (!params[key].type) {
                                if (/^\\d+$/.test(value)) {
                                    params[key].type = 'numeric';
                                } else if (/^(true|false)$/i.test(value)) {
                                    params[key].type = 'boolean';
                                } else if (/^\\d{4}-\\d{2}-\\d{2}/.test(value)) {
                                    params[key].type = 'date';
                                } else {
                                    params[key].type = 'string';
                                }
                            }
                        });
                    } catch(e) {
                        // Invalid URL, skip
                    }
                });

                // Convert Sets to Arrays for JSON serialization
                Object.keys(params).forEach(key => {
                    params[key].values = Array.from(params[key].values);
                    params[key].unique_count = params[key].values.length;
                });

                return params;
            """)

            params = param_data

        except Exception as e:
            self.logger.debug(f"Query parameter extraction error: {e}")

        return params

    def _find_new_elements(self) -> List[Dict[str, Any]]:
        """Find elements that appeared since last check"""
        new_elements = []

        try:
            # Use a different approach - compare element counts and types
            current_state = self.driver.execute_script("""
                const state = {
                    counts: {},
                    samples: []
                };

                // Define what we're looking for
                const interactiveSelectors = [
                    'button',
                    'a[href]',
                    'input:not([type="hidden"])',
                    'select',
                    '[onclick]',
                    '[role="button"]',
                    '[data-action]'
                ];

                // Count each type
                interactiveSelectors.forEach(selector => {
                    const elements = document.querySelectorAll(selector);
                    state.counts[selector] = elements.length;

                    // Sample a few of each type
                    elements.forEach((el, index) => {
                        if (index < 2) {  // First 2 of each type
                            state.samples.push({
                                selector: selector,
                                tag: el.tagName,
                                type: el.type || null,
                                text: el.textContent ? el.textContent.trim().substring(0, 50) : '',
                                href: el.href || null,
                                id: el.id || null,
                                classes: el.className || null,
                                visible: el.offsetParent !== null
                            });
                        }
                    });
                });

                return state;
            """)

            # Compare with previous state if we have one
            if hasattr(self, '_last_element_state'):
                # Find what changed
                for selector, count in current_state['counts'].items():
                    last_count = self._last_element_state.get('counts', {}).get(selector, 0)
                    if count > last_count:
                        # New elements of this type appeared
                        diff = count - last_count
                        self.logger.debug(f"Found {diff} new {selector} elements")

                        # Add samples of new elements
                        for sample in current_state['samples']:
                            if sample['selector'] == selector:
                                new_elements.append({
                                    **sample,
                                    'change_type': 'new',
                                    'count_change': diff
                                })

                # Limit results
                new_elements = new_elements[:20]  # More reasonable limit
            else:
                # First run - everything is "new"
                self.logger.debug("First element scan - establishing baseline")

            # Store current state for next comparison
            self._last_element_state = current_state

        except Exception as e:
            self.logger.debug(f"New element detection error: {e}")

        return new_elements

    # ////

    def _identify_service(self, domain: str) -> str:
        """Identify known services from domain"""
        service_patterns = {
            # Social Media
            'google': ['google.com', 'googleapis.com', 'gstatic.com', 'googleusercontent.com'],
            'facebook': ['facebook.com', 'fbcdn.net', 'fb.com', 'messenger.com'],
            'twitter': ['twitter.com', 't.co', 'twimg.com', 'x.com'],
            'linkedin': ['linkedin.com', 'licdn.com'],
            'reddit': ['reddit.com', 'redd.it', 'redditstatic.com'],
            'youtube': ['youtube.com', 'youtu.be', 'ytimg.com'],
            'tiktok': ['tiktok.com', 'tiktokcdn.com', 'tiktokv.com'],

            # Infrastructure
            'cloudflare': ['cloudflare.com', 'cloudflareinsights.com', 'cf-assets.com'],
            'amazon': ['amazonaws.com', 'amazon.com', 'aws.com', 's3.amazonaws.com'],
            'microsoft': ['microsoft.com', 'msftauth.net', 'azure.com', 'office.com', 'sharepoint.com'],
            'github': ['github.com', 'githubusercontent.com', 'githubapp.com'],

            # CDN/Content
            'cdn': ['cdn.', 'cdnjs.', 'jsdelivr.', 'unpkg.com', 'fastly.net', 'akamai.'],
            'media': ['vimeo.com', 'wistia.com', 'brightcove.', 'jwplayer.com'],

            # Analytics/Tracking
            'analytics': ['google-analytics.com', 'googletagmanager.com', 'segment.com',
                          'mixpanel.com', 'amplitude.com', 'heap.io'],
            'advertising': ['doubleclick.net', 'adsystem.com', 'adnxs.com', 'googlesyndication.com',
                            'facebook.com/tr', 'amazon-adsystem.com'],

            # Government (important for your use case!)
            'government': ['.gov', 'congress.gov', 'senate.gov', 'house.gov',
                           'whitehouse.gov', 'state.gov', 'usa.gov']
        }

        domain_lower = domain.lower()

        # Check for exact domain matches first (more precise)
        for service, patterns in service_patterns.items():
            for pattern in patterns:
                if pattern.startswith('.') and domain_lower.endswith(pattern):
                    return service
                elif pattern in domain_lower:
                    return service

        return 'other'

    def _identify_required_tech(self, report: Dict) -> List[str]:
        """Identify required technologies and packages for scraping"""
        tech = {
            'core': [],
            'data_processing': [],
            'utilities': [],
            'optional': []
        }

        approach = self._determine_best_approach(report)

        # Core scraping tech based on approach
        if approach == 'api_first':
            tech['core'].extend(['requests>=2.28.0', 'json'])
            tech['utilities'].append('urllib3>=1.26.0')  # For better SSL handling
        elif approach == 'static_html':
            tech['core'].extend(['requests>=2.28.0', 'beautifulsoup4>=4.11.0'])
            tech['utilities'].append('lxml>=4.9.0')  # Better parser
        elif approach == 'ajax_monitoring':
            tech['core'].extend(['selenium>=4.0.0', 'requests>=2.28.0'])
            tech['utilities'].append('webdriver-manager>=3.8.0')
        else:  # browser_automation
            tech['core'].extend(['selenium>=4.0.0', 'beautifulsoup4>=4.11.0'])
            tech['utilities'].append('webdriver-manager>=3.8.0')

        # Data processing based on formats
        data_formats = self._identify_data_formats(report)
        if 'csv' in data_formats:
            tech['data_processing'].append('pandas>=1.5.0')
        if 'json' in data_formats:
            tech['utilities'].append('jsonpath-ng>=1.5.0')  # For complex JSON
        if 'xlsx' in data_formats or 'xls' in data_formats:
            tech['data_processing'].extend(['pandas>=1.5.0', 'openpyxl>=3.0.0'])
        if 'xml' in data_formats:
            tech['utilities'].append('xmltodict>=0.13.0')

        # Additional requirements based on features
        if report.get('discovered_features', {}).get('has_login'):
            tech['utilities'].extend(['requests-oauthlib>=1.3.0', 'PyJWT>=2.4.0'])

        if report.get('pagination_patterns', {}).get('has_pagination'):
            tech['utilities'].append('retrying>=1.3.3')  # For retry logic

        if report.get('network_analysis', {}).get('websocket_connections'):
            tech['optional'].append('websocket-client>=1.3.0')

        # If site is complex, recommend monitoring tools
        complexity = report.get('scraper_blueprint', {}).get('metadata', {}).get('complexity_score', 0)
        if complexity > 7:
            tech['optional'].extend(['tqdm>=4.64.0', 'loguru>=0.6.0'])  # Progress & logging

        # Flatten and deduplicate
        all_tech = []
        for category in tech.values():
            all_tech.extend(category)

        return list(dict.fromkeys(all_tech))  # Preserve order while deduping

    def _identify_entry_points(self, report: Dict) -> List[Dict]:
        """Identify best entry points for scraping"""
        entry_points = []

        # 1. Main URL (always first)
        entry_points.append({
            'type': 'main',
            'url': report.get('url', ''),
            'priority': 1,
            'description': 'Primary entry point'
        })

        # 2. Search endpoints (high value)
        search_patterns = report.get('search_patterns', {})
        if search_patterns.get('has_search'):
            # From search forms
            for endpoint in search_patterns.get('search_endpoints', []):
                entry_points.append({
                    'type': 'search',
                    'url': endpoint,
                    'method': 'GET',  # Most search is GET
                    'parameters': list(search_patterns.get('search_parameters', {}).keys()),
                    'priority': 2,
                    'description': 'Search endpoint'
                })

            # From discovered forms
            forms_data = report.get('forms', [])  # This is an array from _discover_all_forms
            for form in forms_data:
                if form.get('purpose') == 'search':  # Using our purpose detection
                    entry_points.append({
                        'type': 'search_form',
                        'url': form.get('action', ''),
                        'method': form.get('method', 'GET'),
                        'parameters': [inp['name'] for inp in form.get('inputs', []) if inp.get('name')],
                        'priority': 2,
                        'description': f'Search form (id: {form.get("id", "unnamed")})'
                    })

        # 3. API endpoints (highest value if available)
        api_endpoints = report.get('network_analysis', {}).get('api_patterns', {})
        for endpoint, data in list(api_endpoints.items())[:5]:  # Top 5
            entry_points.append({
                'type': 'api',
                'url': endpoint,
                'method': 'GET',  # Assume GET unless we know otherwise
                'parameters': list(data.get('parameters', set())),
                'request_count': data.get('count', 0),
                'priority': 1,  # APIs are best!
                'description': f'API endpoint ({data.get("count", 0)} requests observed)'
            })

        # 4. Pagination endpoints
        pagination = report.get('pagination_patterns', {})
        if pagination.get('has_pagination') and pagination.get('url_patterns'):
            for pattern in pagination['url_patterns'][:3]:  # Top 3 patterns
                entry_points.append({
                    'type': 'pagination',
                    'url_pattern': pattern,
                    'priority': 3,
                    'description': f'Pagination pattern ({pagination.get("style", "unknown")} style)'
                })

        # 5. Data export endpoints (from downloadables)
        for download in report.get('downloadable_content', [])[:3]:
            if download.get('type') == 'form_download':
                entry_points.append({
                    'type': 'export',
                    'url': download.get('action', ''),
                    'method': download.get('method', 'POST'),
                    'priority': 2,
                    'description': 'Data export form'
                })

        # Sort by priority
        entry_points.sort(key=lambda x: x.get('priority', 99))

        return entry_points

    def _identify_data_formats(self, report: Dict) -> Dict[str, Any]:
        """Identify data formats available with confidence scores"""
        formats = {
            'confirmed': [],  # Formats we've actually seen
            'likely': [],  # Formats we expect based on patterns
            'possible': []  # Formats that might be available
        }

        # Check API responses for actual content types
        network_analysis = report.get('network_analysis', {})
        api_patterns = network_analysis.get('api_patterns', {})

        for endpoint, data in api_patterns.items():
            # This is where we'd check actual response types
            if 'json' in endpoint or data.get('count', 0) > 0:
                formats['confirmed'].append('json')

        # Check AJAX patterns
        ajax_patterns = report.get('ajax_patterns', {})
        if ajax_patterns.get('captures'):
            for capture in ajax_patterns['captures']:
                if capture.get('response'):
                    # Try to detect format from response
                    try:
                        json.loads(capture['response'])
                        formats['confirmed'].append('json')
                    except:
                        if '<' in capture['response'] and '>' in capture['response']:
                            formats['confirmed'].append('html_fragment')

        # Check for tables
        if report.get('discovered_features', {}).get('table_count', 0) > 0:
            formats['confirmed'].append('html_tables')
            formats['likely'].append('csv')  # Tables often exportable as CSV

        # Check downloadable content
        seen_extensions = set()
        for item in report.get('downloadable_content', []):
            ext = item.get('extension', '').lower()
            if ext and ext != 'unknown':
                seen_extensions.add(ext)

        # Categorize extensions
        for ext in seen_extensions:
            if ext in ['pdf', 'doc', 'docx', 'txt']:
                formats['confirmed'].append(f'document_{ext}')
            elif ext in ['csv', 'xlsx', 'xls']:
                formats['confirmed'].append(f'data_{ext}')
            elif ext in ['json', 'xml']:
                formats['confirmed'].append(f'structured_{ext}')
            elif ext in ['zip', 'rar', '7z']:
                formats['possible'].append(f'archive_{ext}')

        # Check for structured data in page
        baseline = report.get('baseline', {})
        if baseline.get('metadata', {}).get('ldJson'):
            formats['confirmed'].append('json_ld')
        if baseline.get('metadata', {}).get('open_graph'):
            formats['confirmed'].append('open_graph')

        # Deduplicate
        for key in formats:
            formats[key] = list(dict.fromkeys(formats[key]))

        # Create summary
        return {
            'formats': formats,
            'primary_format': formats['confirmed'][0] if formats['confirmed'] else 'html',
            'total_formats': sum(len(v) for v in formats.values()),
            'has_structured_data': bool(formats['confirmed'])
        }

    # ////

    def _detect_technology_stack(self) -> Dict[str, Any]:
        """Detect technology stack of the website"""
        tech_stack = {
            'frontend': {},
            'backend_hints': {},
            'cms': {},
            'analytics': {},
            'security': {},
            'build_tools': {}
        }

        try:
            detected = self.driver.execute_script("""
                const tech = {
                    frontend: {},
                    backend_hints: {},
                    cms: {},
                    analytics: {},
                    security: {},
                    build_tools: {}
                };

                // Frontend frameworks with version detection
                if (typeof jQuery !== 'undefined') {
                    tech.frontend.jquery = jQuery.fn ? jQuery.fn.jquery : true;
                }
                if (typeof React !== 'undefined' || document.querySelector('[data-reactroot]')) {
                    tech.frontend.react = window.React ? (React.version || true) : true;
                }
                if (typeof angular !== 'undefined' || document.querySelector('[ng-app]')) {
                    tech.frontend.angular = window.angular ? (angular.version ? angular.version.full : true) : true;
                }
                if (typeof Vue !== 'undefined' || document.querySelector('[v-cloak]')) {
                    tech.frontend.vue = window.Vue ? (Vue.version || true) : true;
                }

                // Modern frameworks
                if (window.__NEXT_DATA__) tech.frontend.nextjs = true;
                if (window.__NUXT__) tech.frontend.nuxt = true;
                if (window.Svelte) tech.frontend.svelte = true;
                if (window.Alpine) tech.frontend.alpine = true;

                // CSS frameworks
                const stylesheets = Array.from(document.styleSheets);
                if (document.querySelector('[class*="tailwind"]') || 
                    stylesheets.some(s => s.href && s.href.includes('tailwind'))) {
                    tech.frontend.tailwind = true;
                }
                if (document.querySelector('[class*="bootstrap"]') || window.bootstrap) {
                    tech.frontend.bootstrap = window.bootstrap ? (bootstrap.VERSION || true) : true;
                }

                // CMS detection
                const generator = document.querySelector('meta[name="generator"]');
                if (generator) {
                    const content = generator.content.toLowerCase();
                    if (content.includes('wordpress')) tech.cms.wordpress = content;
                    if (content.includes('drupal')) tech.cms.drupal = content;
                    if (content.includes('joomla')) tech.cms.joomla = content;
                    if (content.includes('wix')) tech.cms.wix = content;
                    if (content.includes('squarespace')) tech.cms.squarespace = content;
                }
                if (window.Shopify) tech.cms.shopify = true;
                if (window.TYPO3) tech.cms.typo3 = true;

                // Backend hints from headers/responses
                const responseHeaders = performance.getEntriesByType('navigation')[0];
                if (responseHeaders && responseHeaders.serverTiming) {
                    tech.backend_hints.server_timing = true;
                }

                // Check cookies for backend hints
                if (document.cookie.includes('PHPSESSID')) tech.backend_hints.php = true;
                if (document.cookie.includes('ASP.NET')) tech.backend_hints.aspnet = true;
                if (document.cookie.includes('JSESSIONID')) tech.backend_hints.java = true;
                if (document.cookie.includes('connect.sid')) tech.backend_hints.nodejs = true;

                // Analytics platforms
                if (typeof ga !== 'undefined' || typeof gtag !== 'undefined') {
                    tech.analytics.google_analytics = true;
                }
                if (window._gaq) tech.analytics.google_analytics_classic = true;
                if (window.mixpanel) tech.analytics.mixpanel = true;
                if (window.heap) tech.analytics.heap = true;
                if (window.amplitude) tech.analytics.amplitude = true;
                if (window._paq) tech.analytics.matomo = true;

                // Security/CDN
                if (document.querySelector('script[src*="cloudflare"]') || 
                    window.__CF) {
                    tech.security.cloudflare = true;
                }
                if (window.sucuri) tech.security.sucuri = true;

                // Build tools
                if (document.querySelector('script[src*="webpack"]')) tech.build_tools.webpack = true;
                if (window.Vite) tech.build_tools.vite = true;
                if (window.parcelRequire) tech.build_tools.parcel = true;

                return tech;
            """)

            tech_stack.update(detected)

        except Exception as e:
            self.logger.debug(f"Tech stack detection error: {e}")

        return tech_stack

    def _detect_rate_limits(self) -> Dict:
        """Probe for rate limiting (passive detection only in recon)"""
        rate_limit_info = {
            'detected': False,
            'indicators': [],
            'headers_found': {},
            'response_patterns': [],
            'recommendations': []
        }

        try:
            # Check network data for rate limit indicators
            network_data = self.captured_data.get('network_log', [])

            for request in network_data[-20:]:  # Check recent requests
                # Look for rate limit status codes
                if request.get('status') == 429:
                    rate_limit_info['detected'] = True
                    rate_limit_info['indicators'].append('429 status code observed')

                # Look for rate limit headers
                headers = request.get('headers', {})
                rate_limit_headers = ['x-ratelimit-', 'x-rate-limit-', 'retry-after']

                for header, value in headers.items():
                    if any(rl in header.lower() for rl in rate_limit_headers):
                        rate_limit_info['headers_found'][header] = value
                        rate_limit_info['detected'] = True

            # Analyze response timing patterns
            if len(network_data) > 10:
                response_times = [r.get('duration', 0) for r in network_data if r.get('duration')]
                if response_times:
                    avg_time = sum(response_times) / len(response_times)
                    slow_responses = [t for t in response_times if t > avg_time * 2]

                    if len(slow_responses) > len(response_times) * 0.3:
                        rate_limit_info['indicators'].append('Significant response slowdowns detected')
                        rate_limit_info['response_patterns'].append({
                            'average_ms': avg_time,
                            'slow_count': len(slow_responses),
                            'slow_percentage': len(slow_responses) / len(response_times)
                        })

            # Add recommendations
            if rate_limit_info['detected']:
                rate_limit_info['recommendations'].extend([
                    'Implement exponential backoff',
                    'Respect Retry-After headers',
                    'Consider request pooling',
                    'Monitor response times'
                ])
            else:
                rate_limit_info['recommendations'].append('No rate limiting detected, but implement reasonable delays')

        except Exception as e:
            self.logger.debug(f"Rate limit detection error: {e}")

        return rate_limit_info

    def _detect_barriers(self) -> List[str]:
        """Detect access barriers on the page"""
        barriers = []

        try:
            # Check for common barriers
            barrier_checks = self.driver.execute_script("""
                const barriers = [];
                const foundElements = {};  // Track what we found

                // Paywall detection - ENHANCED
                const paywallSelectors = [
                    '.paywall', '[class*="paywall"]', '[id*="paywall"]',
                    '.subscription-wall', '.premium-wall', '.meter-wall',
                    '.subscriber-only', '[class*="premium-content"]',
                    '.article-lock', '.content-gate'
                ];

                paywallSelectors.forEach(selector => {
                    const el = document.querySelector(selector);
                    if (el && window.getComputedStyle(el).display !== 'none') {
                        barriers.push('paywall_detected');
                        foundElements.paywall = selector;
                    }
                });

                // Login requirement - IMPROVED LOGIC
                const hasPasswordField = document.querySelector('input[type="password"]');
                const hasMainContent = document.querySelector('main, article, [role="main"]');
                const loginKeywords = ['login', 'sign in', 'log in', 'signin'];
                const pageText = document.body.textContent.toLowerCase();

                if (hasPasswordField && !hasMainContent && 
                    loginKeywords.some(kw => pageText.includes(kw))) {
                    barriers.push('login_required');
                }

                // Cookie banners - ENHANCED
                const cookieSelectors = [
                    '.cookie-banner', '#cookie-consent', '[class*="cookie"]',
                    '.gdpr-banner', '[class*="gdpr"]', '.consent-banner',
                    '[class*="privacy-notice"]', '.cc-window'  // CookieConsent library
                ];

                cookieSelectors.forEach(selector => {
                    const el = document.querySelector(selector);
                    if (el && window.getComputedStyle(el).display !== 'none') {
                        barriers.push('cookie_banner');
                        foundElements.cookie = selector;
                    }
                });

                // Overlay modals - BETTER DETECTION
                const overlays = document.querySelectorAll('[class*="modal"], [class*="overlay"], .popup, [role="dialog"]');
                overlays.forEach(el => {
                    const style = window.getComputedStyle(el);
                    const rect = el.getBoundingClientRect();

                    // Check if it's actually visible and blocking
                    if (style.position === 'fixed' && 
                        style.display !== 'none' && 
                        rect.width > 0 && 
                        rect.height > 0 &&
                        (rect.width > window.innerWidth * 0.5 || rect.height > window.innerHeight * 0.5)) {
                        barriers.push('overlay_modal');
                        foundElements.overlay = el.className;
                    }
                });

                // Blur effects on content
                document.querySelectorAll('*').forEach(el => {
                    const style = window.getComputedStyle(el);
                    if (style.filter && style.filter.includes('blur') && el.textContent.length > 100) {
                        barriers.push('content_blur');
                        foundElements.blur = el.tagName;
                    }
                });

                // Disabled interactions
                if (document.oncontextmenu !== null) {
                    barriers.push('right_click_disabled');
                }
                if (document.onselectstart !== null) {
                    barriers.push('text_selection_disabled');
                }

                // Age gate detection
                if (document.querySelector('[class*="age-gate"], [class*="age-verification"], #age-gate')) {
                    barriers.push('age_verification');
                }

                // Region blocking
                if (pageText.includes('not available in your') || 
                    pageText.includes('blocked in your region')) {
                    barriers.push('region_blocked');
                }

                return {
                    barriers: [...new Set(barriers)],  // Remove duplicates
                    elements: foundElements  // Return what we found for debugging
                };
            """)

            barriers = barrier_checks['barriers']

            # Log what elements were found for debugging
            if barrier_checks.get('elements'):
                self.logger.debug(f"Barrier elements found: {barrier_checks['elements']}")

        except Exception as e:
            self.logger.debug(f"Barrier detection error: {e}")

        return barriers

    def _detect_state_changes(self, before: Dict, after: Dict) -> List[str]:
        """Detect what changed between states"""
        changes = []

        # URL changes
        if before.get('url') != after.get('url'):
            changes.append(f"URL changed from {before.get('url')} to {after.get('url')}")

        # Element count changes
        elem_diff = after.get('element_count', 0) - before.get('element_count', 0)
        if abs(elem_diff) > 5:  # Only report significant changes
            if elem_diff > 0:
                changes.append(f"Added {elem_diff} elements")
            else:
                changes.append(f"Removed {abs(elem_diff)} elements")

        # Text content changes
        text_diff = after.get('body_length', 0) - before.get('body_length', 0)
        if abs(text_diff) > 100:  # Significant text change
            if text_diff > 0:
                changes.append(f"Added ~{text_diff} characters of text")
            else:
                changes.append(f"Removed ~{abs(text_diff)} characters of text")

        # Cookie changes
        cookie_diff = after.get('cookies', 0) - before.get('cookies', 0)
        if cookie_diff > 0:
            changes.append(f"{cookie_diff} new cookies set")
        elif cookie_diff < 0:
            changes.append(f"{abs(cookie_diff)} cookies removed")

        # Storage changes
        storage_before = before.get('local_storage_items', 0)
        storage_after = after.get('local_storage_items', 0)
        if storage_before != storage_after:
            changes.append(f"LocalStorage changed from {storage_before} to {storage_after} items")

        # Title change
        if before.get('title') != after.get('title'):
            changes.append(f"Page title changed to: {after.get('title')}")

        return changes

    def _detect_id_formats(self) -> Dict[str, Any]:
        """Detect ID formats used in the site"""
        formats = {
            'patterns': {},
            'examples': {},
            'statistics': {
                'total_found': 0,
                'unique_patterns': 0
            }
        }

        try:
            # Check various ID patterns
            id_data = self.driver.execute_script("""
                const idData = {
                    examples: [],
                    locations: {}
                };

                // Check data attributes - EXPANDED
                const dataSelectors = [
                    '[data-id]', '[data-item-id]', '[data-product-id]',
                    '[data-user-id]', '[data-post-id]', '[data-article-id]',
                    '[data-entity-id]', '[data-record-id]', '[data-object-id]'
                ];

                dataSelectors.forEach(selector => {
                    document.querySelectorAll(selector).forEach(el => {
                        Object.keys(el.dataset).forEach(key => {
                            if (key.toLowerCase().includes('id')) {
                                const value = el.dataset[key];
                                if (value && value.length > 0) {
                                    idData.examples.push({
                                        value: value,
                                        source: 'data-attribute',
                                        attribute: key,
                                        tag: el.tagName
                                    });
                                }
                            }
                        });
                    });
                });

                // Check URL patterns - IMPROVED
                const urlPatterns = [
                    /\\/([a-zA-Z0-9_-]+)\\/?(\\?|$|#)/,  // ID at end of path
                    /\\/(?:item|product|post|article|user|id)\\/([a-zA-Z0-9_-]+)/i,  // After keyword
                    /[?&]id=([a-zA-Z0-9_-]+)/,  // Query parameter
                    /\\/([0-9]{4,})/,  // Numeric IDs in path
                    /\\/([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/i  // UUIDs
                ];

                document.querySelectorAll('a[href]').forEach(a => {
                    urlPatterns.forEach(pattern => {
                        const matches = a.href.match(pattern);
                        if (matches && matches[1]) {
                            idData.examples.push({
                                value: matches[1],
                                source: 'url',
                                pattern: pattern.source,
                                full_url: a.href
                            });
                        }
                    });
                });

                // Check form inputs
                document.querySelectorAll('input[name*="id"], input[id*="id"]').forEach(input => {
                    if (input.value) {
                        idData.examples.push({
                            value: input.value,
                            source: 'form-input',
                            name: input.name || input.id
                        });
                    }
                });

                // Deduplicate and limit
                const seen = new Set();
                const unique = [];
                for (const example of idData.examples) {
                    if (!seen.has(example.value)) {
                        seen.add(example.value);
                        unique.push(example);
                        if (unique.length >= 50) break;  // Limit to 50
                    }
                }

                return unique;
            """)

            formats['statistics']['total_found'] = len(id_data)

            # Analyze formats with better categorization
            for item in id_data:
                id_value = item['value']
                pattern_type = None

                # Detect pattern type
                if re.match(r'^\d+$', id_value):
                    pattern_type = f"numeric_{len(id_value)}_digits"
                    pattern_desc = f"Numeric: {len(id_value)} digits"
                elif re.match(r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$', id_value, re.I):
                    pattern_type = "uuid_v4"
                    pattern_desc = "UUID v4 format"
                elif re.match(r'^[a-f0-9]{24}$', id_value, re.I):
                    pattern_type = "mongodb_objectid"
                    pattern_desc = "MongoDB ObjectId format"
                elif re.match(r'^[A-Z0-9]{8,}$', id_value):
                    pattern_type = "uppercase_alphanumeric"
                    pattern_desc = f"Uppercase alphanumeric: {len(id_value)} chars"
                elif '-' in id_value:
                    pattern_type = "hyphenated"
                    pattern_desc = f"Hyphenated format: {len(id_value)} chars"
                elif '_' in id_value:
                    pattern_type = "underscore_separated"
                    pattern_desc = f"Underscore format: {len(id_value)} chars"
                else:
                    pattern_type = f"alphanumeric_{len(id_value)}"
                    pattern_desc = f"Alphanumeric: {len(id_value)} chars"

                # Store pattern info
                if pattern_type not in formats['patterns']:
                    formats['patterns'][pattern_type] = {
                        'description': pattern_desc,
                        'count': 0,
                        'sources': set()
                    }

                formats['patterns'][pattern_type]['count'] += 1
                formats['patterns'][pattern_type]['sources'].add(item['source'])

                # Store examples (max 3 per pattern)
                if pattern_type not in formats['examples']:
                    formats['examples'][pattern_type] = []
                if len(formats['examples'][pattern_type]) < 3:
                    formats['examples'][pattern_type].append({
                        'value': id_value,
                        'source': item['source'],
                        'context': item.get('full_url', item.get('attribute', ''))
                    })

            # Convert sets to lists for JSON serialization
            for pattern in formats['patterns'].values():
                pattern['sources'] = list(pattern['sources'])

            formats['statistics']['unique_patterns'] = len(formats['patterns'])

        except Exception as e:
            self.logger.debug(f"ID format detection error: {e}")

        return formats

    def _detect_dom_changes(self) -> Dict[str, Any]:
        """Detect what changed in the DOM since last capture"""
        changes = {
            'summary': [],
            'details': {},
            'performance_impact': {},
            'significant_changes': False
        }

        try:
            # Get current DOM stats - ENHANCED
            current_stats = self.driver.execute_script("""
                // Helper to safely hash content
                function safeHash(str) {
                    try {
                        // Simple hash for change detection
                        let hash = 0;
                        for (let i = 0; i < Math.min(str.length, 1000); i++) {
                            const char = str.charCodeAt(i);
                            hash = ((hash << 5) - hash) + char;
                            hash = hash & hash; // Convert to 32bit integer
                        }
                        return hash.toString(16);
                    } catch(e) {
                        return 'error';
                    }
                }

                const stats = {
                    // Basic counts
                    total_elements: document.querySelectorAll('*').length,
                    images: document.images.length,
                    links: document.links.length,
                    forms: document.forms.length,
                    scripts: document.scripts.length,
                    iframes: document.querySelectorAll('iframe').length,

                    // Content metrics
                    body_length: document.body.textContent.length,
                    body_hash: safeHash(document.body.innerHTML),

                    // Interactive elements
                    buttons: document.querySelectorAll('button').length,
                    inputs: document.querySelectorAll('input, textarea, select').length,

                    // Dynamic content indicators
                    ajax_elements: document.querySelectorAll('[data-ajax], [data-load]').length,
                    lazy_images: document.querySelectorAll('img[data-src], img.lazy').length,

                    // Performance metrics
                    dom_depth: (function() {
                        let maxDepth = 0;
                        function getDepth(element, depth = 0) {
                            maxDepth = Math.max(maxDepth, depth);
                            for (let child of element.children) {
                                getDepth(child, depth + 1);
                            }
                        }
                        getDepth(document.body);
                        return maxDepth;
                    })(),

                    // Visibility
                    hidden_elements: document.querySelectorAll('[style*="display: none"], [hidden]').length,

                    // Timestamp
                    timestamp: Date.now()
                };

                return stats;
            """)

            # Compare with last snapshot if exists
            if hasattr(self, '_last_dom_stats'):
                last_stats = self._last_dom_stats
                time_diff = (current_stats['timestamp'] - last_stats.get('timestamp', 0)) / 1000  # seconds

                # Analyze each metric
                for key, current_value in current_stats.items():
                    if key == 'timestamp':
                        continue

                    if key in last_stats:
                        last_value = last_stats[key]

                        if current_value != last_value:
                            if isinstance(current_value, (int, float)):
                                change = current_value - last_value
                                change_pct = (change / last_value * 100) if last_value > 0 else 0

                                change_info = {
                                    'type': key,
                                    'previous': last_value,
                                    'current': current_value,
                                    'change': change,
                                    'change_percent': round(change_pct, 1),
                                    'rate_per_second': round(change / time_diff, 2) if time_diff > 0 else 0
                                }

                                # Categorize change significance
                                if abs(change_pct) > 50:
                                    change_info['significance'] = 'major'
                                    changes['significant_changes'] = True
                                elif abs(change_pct) > 20:
                                    change_info['significance'] = 'moderate'
                                else:
                                    change_info['significance'] = 'minor'

                                changes['details'][key] = change_info

                                # Create human-readable summary
                                if change > 0:
                                    changes['summary'].append(f"Added {change} {key.replace('_', ' ')}")
                                elif change < 0:
                                    changes['summary'].append(f"Removed {abs(change)} {key.replace('_', ' ')}")
                            else:
                                # Non-numeric change (like hash)
                                changes['details'][key] = {
                                    'type': key,
                                    'changed': True,
                                    'previous': last_value,
                                    'current': current_value
                                }
                                changes['summary'].append(f"{key.replace('_', ' ')} modified")

                # Performance impact analysis
                if current_stats['total_elements'] > last_stats.get('total_elements', 0) * 1.5:
                    changes['performance_impact']['dom_growth'] = 'High - DOM size increased significantly'

                if current_stats['dom_depth'] > 32:
                    changes['performance_impact'][
                        'dom_depth'] = f'Warning - DOM depth is {current_stats["dom_depth"]} (>32 can impact performance)'

                if current_stats['scripts'] > last_stats.get('scripts', 0):
                    changes['performance_impact'][
                        'new_scripts'] = f'Added {current_stats["scripts"] - last_stats.get("scripts", 0)} scripts'

            else:
                # First capture
                changes['summary'].append("Initial DOM capture")
                self.logger.debug("First DOM capture - establishing baseline")

            # Store current state for next comparison
            self._last_dom_stats = current_stats

        except Exception as e:
            self.logger.debug(f"DOM change detection error: {e}")
            changes['error'] = str(e)

        return changes

    # ////

    def _extract_all_metadata(self) -> Dict:
        """Extract ALL metadata from the page"""
        try:
            metadata_script = """
            const metadata = {
                // Basic page info
                page_info: {
                    title: document.title,
                    url: window.location.href,
                    charset: document.characterSet,
                    language: document.documentElement.lang || 'unknown',
                    lastModified: document.lastModified
                },
                // Meta tags
                meta_tags: {},
                // Link tags
                link_tags: [],
                // OpenGraph
                open_graph: {},
                // Twitter Cards
                twitter_cards: {},
                // JSON-LD
                json_ld: [],
                // Microdata/Schema.org
                microdata: [],
                // Dublin Core
                dublin_core: {},
                // Data attributes on root elements
                root_data: {},
                // Other structured data
                structured_data: {
                    rdfa: [],
                    microformats: []
                }
            };

            // Meta tags - COMPREHENSIVE
            document.querySelectorAll('meta').forEach(meta => {
                // Get all possible name attributes
                const name = meta.getAttribute('name') || 
                            meta.getAttribute('property') || 
                            meta.getAttribute('http-equiv') ||
                            meta.getAttribute('itemprop');

                if (name && meta.content) {
                    metadata.meta_tags[name] = meta.content;

                    // Categorize special types
                    if (name.startsWith('og:')) {
                        metadata.open_graph[name] = meta.content;
                    } else if (name.startsWith('twitter:')) {
                        metadata.twitter_cards[name] = meta.content;
                    } else if (name.startsWith('DC.') || name.startsWith('dc.')) {
                        metadata.dublin_core[name] = meta.content;
                    }
                }

                // Special handling for charset
                if (meta.charset) {
                    metadata.page_info.charset = meta.charset;
                }
            });

            // Link tags - ENHANCED
            document.querySelectorAll('link').forEach(link => {
                const linkData = {
                    rel: link.rel,
                    href: link.href,
                    type: link.type || null,
                    media: link.media || null,
                    sizes: link.sizes ? link.sizes.toString() : null,
                    title: link.title || null,
                    hreflang: link.hreflang || null,
                    as: link.as || null,  // For preload/prefetch
                    crossorigin: link.crossOrigin || null
                };

                // Only add non-null properties
                const cleanLink = {};
                Object.keys(linkData).forEach(key => {
                    if (linkData[key] !== null && linkData[key] !== '') {
                        cleanLink[key] = linkData[key];
                    }
                });

                metadata.link_tags.push(cleanLink);
            });

            // JSON-LD - WITH VALIDATION
            document.querySelectorAll('script[type="application/ld+json"]').forEach(script => {
                try {
                    const data = JSON.parse(script.textContent);
                    // Add source info
                    metadata.json_ld.push({
                        data: data,
                        context: data['@context'] || null,
                        type: data['@type'] || null,
                        valid: true
                    });
                } catch(e) {
                    // Store invalid JSON-LD for debugging
                    metadata.json_ld.push({
                        raw: script.textContent.substring(0, 200) + '...',
                        error: e.message,
                        valid: false
                    });
                }
            });

            // Microdata extraction - IMPLEMENTED!
            document.querySelectorAll('[itemscope]').forEach(item => {
                const microdataItem = {
                    type: item.getAttribute('itemtype'),
                    properties: {}
                };

                // Find all properties within this scope
                item.querySelectorAll('[itemprop]').forEach(prop => {
                    const propName = prop.getAttribute('itemprop');
                    let value = prop.content || prop.textContent || prop.href || prop.src;

                    if (propName) {
                        if (!microdataItem.properties[propName]) {
                            microdataItem.properties[propName] = [];
                        }
                        microdataItem.properties[propName].push(value);
                    }
                });

                if (Object.keys(microdataItem.properties).length > 0) {
                    metadata.microdata.push(microdataItem);
                }
            });

            // RDFa detection
            document.querySelectorAll('[typeof], [property], [vocab]').forEach(el => {
                if (el.hasAttribute('typeof') || el.hasAttribute('property')) {
                    metadata.structured_data.rdfa.push({
                        typeof: el.getAttribute('typeof'),
                        property: el.getAttribute('property'),
                        content: el.getAttribute('content') || el.textContent.substring(0, 100)
                    });
                }
            });

            // Microformats detection
            const microformatClasses = ['h-card', 'h-entry', 'h-event', 'h-review', 'h-recipe'];
            microformatClasses.forEach(mfClass => {
                document.querySelectorAll('.' + mfClass).forEach(el => {
                    metadata.structured_data.microformats.push({
                        type: mfClass,
                        properties: el.className
                    });
                });
            });

            // Root element data attributes - ENHANCED
            ['html', 'body'].forEach(tag => {
                const el = document.querySelector(tag);
                if (el) {
                    metadata.root_data[tag] = {
                        attributes: {},
                        classes: el.className || '',
                        id: el.id || ''
                    };

                    // Get all attributes
                    for (let attr of el.attributes) {
                        if (attr.name.startsWith('data-') || 
                            ['lang', 'dir', 'class', 'id'].includes(attr.name)) {
                            metadata.root_data[tag].attributes[attr.name] = attr.value;
                        }
                    }
                }
            });

            // Additional semantic data
            metadata.semantic = {
                // Check for AMP
                is_amp: document.querySelector('html[amp]') !== null,
                // Check for PWA
                has_manifest: document.querySelector('link[rel="manifest"]') !== null,
                // Check for RSS/Atom feeds
                has_feeds: document.querySelectorAll('link[type*="rss"], link[type*="atom"]').length > 0,
                // Canonical URL
                canonical: document.querySelector('link[rel="canonical"]')?.href || null,
                // Favicon
                favicon: document.querySelector('link[rel="icon"], link[rel="shortcut icon"]')?.href || null
            };

            // Statistics
            metadata.stats = {
                meta_count: Object.keys(metadata.meta_tags).length,
                link_count: metadata.link_tags.length,
                json_ld_count: metadata.json_ld.filter(j => j.valid).length,
                microdata_count: metadata.microdata.length,
                has_open_graph: Object.keys(metadata.open_graph).length > 0,
                has_twitter_cards: Object.keys(metadata.twitter_cards).length > 0,
                has_structured_data: metadata.json_ld.length > 0 || metadata.microdata.length > 0
            };

            return metadata;
            """

            metadata = self.driver.execute_script(metadata_script)

            # Post-process to ensure clean data
            if metadata:
                # Validate and clean JSON-LD
                valid_json_ld = []
                for item in metadata.get('json_ld', []):
                    if item.get('valid') and item.get('data'):
                        valid_json_ld.append(item['data'])
                metadata['json_ld'] = valid_json_ld

                # Log summary
                self.logger.info(f"[METADATA] Extracted: {metadata.get('stats', {})}")

            return metadata

        except Exception as e:
            self.logger.error(f"Metadata extraction error: {e}")
            return {
                'error': str(e),
                'page_info': {'title': 'Error', 'url': self.driver.current_url},
                'meta_tags': {},
                'link_tags': [],
                'open_graph': {},
                'twitter_cards': {},
                'json_ld': [],
                'microdata': [],
                'stats': {}
            }

    # ////

    def _analyze_url_structures(self) -> Dict:
        """Understand URL patterns for direct access"""
        url_patterns = {
            'base_patterns': self._extract_url_patterns(),
            'parameter_patterns': self._find_query_parameters(),
            'path_structures': self._analyze_path_patterns(),
            'id_formats': self._detect_id_formats()
        }
        return url_patterns

    def _analyze_data_structures(self) -> Dict[str, Any]:
        """Analyze data structures on the page for scraping intelligence"""
        structures = {
            'tables': {
                'count': 0,
                'details': [],
                'has_data_tables': False,
                'has_layout_tables': False
            },
            'lists': {
                'count': 0,
                'types': {'ordered': 0, 'unordered': 0, 'definition': 0},
                'nested_depth': 0,
                'data_lists': []
            },
            'structured_data': {
                'json_ld': {'count': 0, 'types': []},
                'microdata': {'count': 0, 'types': []},
                'rdfa': {'count': 0}
            },
            'data_patterns': {
                'repeating_structures': [],
                'data_containers': [],
                'grid_layouts': []
            },
            'extraction_complexity': 'low'
        }

        try:
            analysis = self.driver.execute_script("""
                const analysis = {
                    tables: {details: []},
                    lists: {details: []},
                    patterns: {containers: [], grids: []}
                };

                // TABLES - Deep analysis
                document.querySelectorAll('table').forEach((table, idx) => {
                    const tableInfo = {
                        index: idx,
                        rows: table.rows.length,
                        cols: table.rows[0] ? table.rows[0].cells.length : 0,
                        has_header: false,
                        has_footer: false,
                        purpose: 'unknown',
                        data_quality: {},
                        classes: table.className,
                        id: table.id
                    };

                    // Check for headers
                    if (table.querySelector('thead') || table.querySelector('th')) {
                        tableInfo.has_header = true;

                        // Extract header text
                        const headers = Array.from(table.querySelectorAll('th')).map(th => th.textContent.trim());
                        tableInfo.headers = headers;
                    }

                    // Check for footer
                    if (table.querySelector('tfoot')) {
                        tableInfo.has_footer = true;
                    }

                    // Determine table purpose
                    if (tableInfo.rows > 3 && tableInfo.has_header) {
                        tableInfo.purpose = 'data';

                        // Analyze data quality
                        let emptyCells = 0;
                        let totalCells = 0;

                        table.querySelectorAll('td').forEach(td => {
                            totalCells++;
                            if (!td.textContent.trim()) emptyCells++;
                        });

                        tableInfo.data_quality = {
                            empty_cells: emptyCells,
                            total_cells: totalCells,
                            completeness: totalCells > 0 ? (totalCells - emptyCells) / totalCells : 0
                        };
                    } else if (tableInfo.rows === 1 || tableInfo.cols === 1) {
                        tableInfo.purpose = 'layout';
                    }

                    analysis.tables.details.push(tableInfo);
                });

                // LISTS - Deep analysis
                let maxNesting = 0;

                function analyzeList(list, depth = 0) {
                    maxNesting = Math.max(maxNesting, depth);

                    const listInfo = {
                        type: list.tagName.toLowerCase(),
                        items: list.children.length,
                        depth: depth,
                        has_nested: list.querySelector('ul, ol') !== null,
                        classes: list.className,
                        parent_context: list.parentElement ? list.parentElement.tagName : null
                    };

                    // Check if it's a data list (not navigation)
                    const isNav = list.closest('nav') !== null;
                    const isMenu = list.className.includes('menu') || list.className.includes('nav');

                    if (!isNav && !isMenu && listInfo.items > 3) {
                        listInfo.purpose = 'data';

                        // Sample first few items
                        listInfo.sample_items = Array.from(list.children).slice(0, 3).map(li => ({
                            text: li.textContent.trim().substring(0, 100),
                            has_links: li.querySelector('a') !== null,
                            has_nested_data: li.children.length > 1
                        }));
                    } else {
                        listInfo.purpose = 'navigation';
                    }

                    analysis.lists.details.push(listInfo);

                    // Recurse into nested lists
                    list.querySelectorAll(':scope > li > ul, :scope > li > ol').forEach(nested => {
                        analyzeList(nested, depth + 1);
                    });
                }

                // Analyze all top-level lists
                document.querySelectorAll('ul:not(li ul), ol:not(li ol), dl').forEach(list => {
                    analyzeList(list);
                });

                analysis.lists.max_nesting = maxNesting;

                // DATA PATTERNS - Find repeating structures
                // Look for repeated class patterns
                const classOccurrences = {};
                document.querySelectorAll('[class]').forEach(el => {
                    const classes = el.className.split(/\\s+/).filter(c => c.length > 2);
                    classes.forEach(cls => {
                        if (!classOccurrences[cls]) classOccurrences[cls] = [];
                        classOccurrences[cls].push({
                            tag: el.tagName,
                            parent: el.parentElement ? el.parentElement.tagName : null
                        });
                    });
                });

                // Find repeating patterns
                Object.entries(classOccurrences).forEach(([cls, elements]) => {
                    if (elements.length > 3) {
                        // Check if they're siblings
                        const parents = new Set(elements.map(e => e.parent));
                        if (parents.size === 1) {
                            analysis.patterns.containers.push({
                                class: cls,
                                count: elements.length,
                                tag: elements[0].tag,
                                parent: elements[0].parent,
                                likely_data_items: true
                            });
                        }
                    }
                });

                // Find grid-like structures
                document.querySelectorAll('[class*="grid"], [class*="row"], [class*="col"]').forEach(el => {
                    const children = el.children;
                    if (children.length > 2) {
                        // Check if children have similar structure
                        const firstChildTags = Array.from(children[0].children).map(c => c.tagName);
                        let similar = true;

                        for (let i = 1; i < Math.min(children.length, 5); i++) {
                            const childTags = Array.from(children[i].children).map(c => c.tagName);
                            if (childTags.join(',') !== firstChildTags.join(',')) {
                                similar = false;
                                break;
                            }
                        }

                        if (similar) {
                            analysis.patterns.grids.push({
                                class: el.className,
                                item_count: children.length,
                                structure_per_item: firstChildTags
                            });
                        }
                    }
                });

                // Structured data counts
                analysis.json_ld_count = document.querySelectorAll('script[type="application/ld+json"]').length;
                analysis.microdata_count = document.querySelectorAll('[itemscope]').length;
                analysis.rdfa_count = document.querySelectorAll('[typeof], [property]').length;

                return analysis;
            """)

            # Process JavaScript results
            if analysis.get('tables', {}).get('details'):
                structures['tables']['count'] = len(analysis['tables']['details'])
                structures['tables']['details'] = analysis['tables']['details']

                # Categorize tables
                for table in analysis['tables']['details']:
                    if table.get('purpose') == 'data':
                        structures['tables']['has_data_tables'] = True
                    elif table.get('purpose') == 'layout':
                        structures['tables']['has_layout_tables'] = True

            if analysis.get('lists', {}).get('details'):
                structures['lists']['count'] = len(analysis['lists']['details'])
                structures['lists']['nested_depth'] = analysis['lists'].get('max_nesting', 0)

                # Count list types and find data lists
                for lst in analysis['lists']['details']:
                    list_type = lst.get('type', 'ul')
                    if list_type == 'ul':
                        structures['lists']['types']['unordered'] += 1
                    elif list_type == 'ol':
                        structures['lists']['types']['ordered'] += 1
                    elif list_type == 'dl':
                        structures['lists']['types']['definition'] += 1

                    if lst.get('purpose') == 'data':
                        structures['lists']['data_lists'].append(lst)

            # Process patterns
            if analysis.get('patterns', {}).get('containers'):
                structures['data_patterns']['repeating_structures'] = analysis['patterns']['containers']

            if analysis.get('patterns', {}).get('grids'):
                structures['data_patterns']['grid_layouts'] = analysis['patterns']['grids']

            # Structured data
            structures['structured_data']['json_ld']['count'] = analysis.get('json_ld_count', 0)
            structures['structured_data']['microdata']['count'] = analysis.get('microdata_count', 0)
            structures['structured_data']['rdfa']['count'] = analysis.get('rdfa_count', 0)

            # Assess extraction complexity
            complexity_score = 0

            if structures['tables']['has_data_tables']:
                complexity_score += 1
            if structures['lists']['data_lists']:
                complexity_score += 1
            if structures['data_patterns']['repeating_structures']:
                complexity_score += 2
            if structures['structured_data']['json_ld']['count'] > 0:
                complexity_score -= 1  # JSON-LD makes it easier

            if complexity_score <= 1:
                structures['extraction_complexity'] = 'low'
            elif complexity_score <= 3:
                structures['extraction_complexity'] = 'medium'
            else:
                structures['extraction_complexity'] = 'high'

        except Exception as e:
            self.logger.debug(f"Data structure analysis error: {e}")

        return structures

    def _assess_transformation_needs(self, report: Dict) -> Dict:
        """Assess what data transformations are needed"""
        needs = {
            'cleaning': {
                'required': True,  # Always assume some cleaning
                'types': []
            },
            'format_conversion': {
                'required': False,
                'from_formats': [],
                'to_formats': []
            },
            'deduplication': {
                'required': False,
                'reason': None
            },
            'normalization': {
                'required': False,
                'fields': []
            },
            'enrichment': {
                'required': False,
                'types': []
            }
        }

        # Assess cleaning needs based on data structures
        data_structures = report.get('data_structures', {})

        # Check table data quality
        for table in data_structures.get('tables', {}).get('details', []):
            if table.get('data_quality', {}).get('completeness', 1) < 0.9:
                needs['cleaning']['types'].append('missing_data')
                needs['cleaning']['types'].append('empty_cells')

        # Check for common cleaning needs
        if report.get('discovered_features', {}).get('has_javascript'):
            needs['cleaning']['types'].append('javascript_rendered_content')

        if report.get('access_barriers', []):
            needs['cleaning']['types'].append('remove_artifacts_from_barriers')

        # Format conversion needs
        data_formats = report.get('technical_insights', {}).get('data_formats', [])

        if 'html_tables' in data_formats:
            needs['format_conversion']['required'] = True
            needs['format_conversion']['from_formats'].append('html_tables')
            needs['format_conversion']['to_formats'].extend(['csv', 'json', 'dataframe'])

        if 'json_ld' in data_formats:
            needs['format_conversion']['from_formats'].append('json_ld')
            needs['format_conversion']['to_formats'].append('normalized_json')

        # Deduplication needs
        pagination = report.get('pagination_patterns', {})
        if pagination.get('has_pagination'):
            needs['deduplication']['required'] = True
            needs['deduplication']['reason'] = f"Pagination detected ({pagination.get('style', 'unknown')} style)"

        # Check for infinite scroll
        if pagination.get('style') == 'infinite':
            needs['deduplication']['required'] = True
            needs['deduplication']['reason'] = 'Infinite scroll may load duplicate items'

        # Normalization needs
        forms_data = report.get('forms', [])  # Array from _discover_all_forms
        search_forms = [f for f in forms_data if f.get('purpose') == 'search']

        if len(search_forms) > 1:
            needs['normalization']['required'] = True
            needs['normalization']['fields'].append('search_parameters')

        # Check for multiple data sources
        if (data_structures.get('tables', {}).get('count', 0) > 0 and
                data_structures.get('structured_data', {}).get('json_ld', {}).get('count', 0) > 0):
            needs['normalization']['required'] = True
            needs['normalization']['fields'].append('cross_source_data_merge')

        # Enrichment needs
        if not data_structures.get('structured_data', {}).get('json_ld', {}).get('count', 0):
            needs['enrichment']['types'].append('add_metadata')
            needs['enrichment']['required'] = True

        # ID format variety suggests normalization
        id_formats = report.get('url_patterns', {}).get('id_formats', [])
        if isinstance(id_formats, dict):  # Our enhanced version returns dict
            if id_formats.get('statistics', {}).get('unique_patterns', 0) > 2:
                needs['normalization']['required'] = True
                needs['normalization']['fields'].append('id_format_standardization')

        # Remove duplicates from lists
        for key in ['cleaning', 'format_conversion']:
            if 'types' in needs[key]:
                needs[key]['types'] = list(set(needs[key]['types']))
            if 'from_formats' in needs[key]:
                needs[key]['from_formats'] = list(set(needs[key]['from_formats']))
            if 'to_formats' in needs[key]:
                needs[key]['to_formats'] = list(set(needs[key]['to_formats']))

        return needs

    def _assess_concurrency_safety(self, report: Dict) -> Dict[str, Any]:
        """Assess if concurrent scraping is safe and provide recommendations"""
        assessment = {
            'safe': True,
            'risk_level': 'low',  # low, medium, high
            'max_concurrent': 1,
            'recommended_delay': 2,
            'factors': {
                'positive': [],  # Factors that suggest safety
                'negative': []  # Factors that suggest caution
            },
            'recommendations': []
        }

        # Check negative factors (reduce safety)

        # 1. Rate limiting
        rate_limits = report.get('rate_limits', {})
        if rate_limits.get('detected'):
            assessment['safe'] = False
            assessment['risk_level'] = 'high'
            assessment['factors']['negative'].append('Rate limiting detected')
            assessment['recommendations'].append('Use single-threaded scraping with delays')

        # 2. Authentication required
        if report.get('discovered_features', {}).get('has_login'):
            assessment['max_concurrent'] = 1
            assessment['factors']['negative'].append('Authentication required - session management needed')
            assessment['recommendations'].append('Use session pooling if concurrent')

        # 3. Cloudflare or anti-bot
        barriers = report.get('access_barriers', [])
        tech_stack = report.get('tech_stack', {})

        if 'cloudflare' in str(barriers).lower() or tech_stack.get('security', {}).get('cloudflare'):
            assessment['safe'] = False
            assessment['risk_level'] = 'high'
            assessment['factors']['negative'].append('Cloudflare protection detected')
            assessment['recommendations'].append('Use rotating proxies and browser automation')

        # 4. Complex JavaScript
        if report.get('ajax_patterns', {}).get('captures'):
            assessment['max_concurrent'] = min(assessment['max_concurrent'], 3)
            assessment['factors']['negative'].append('Dynamic content requires careful timing')

        # 5. Server response times
        network_stats = report.get('network_analysis', {}).get('statistics', {})
        avg_response_time = network_stats.get('avg_response_time', 0)

        if avg_response_time > 1000:  # Over 1 second average
            assessment['factors']['negative'].append(f'Slow server response ({avg_response_time:.0f}ms avg)')
            assessment['recommended_delay'] = max(3, avg_response_time / 1000 * 2)

        # 6. Shared resources (database-driven sites)
        if report.get('tech_stack', {}).get('cms', {}).get('wordpress'):
            assessment['factors']['negative'].append('CMS detected - likely shared hosting')
            assessment['max_concurrent'] = min(assessment['max_concurrent'], 2)

        # Check positive factors (increase safety)

        # 1. Static content
        if not report.get('site_structure', {}).get('content_delivery', {}).get('requires_javascript'):
            assessment['factors']['positive'].append('Static content - easier to parallelize')
            assessment['max_concurrent'] = max(assessment['max_concurrent'], 5)

        # 2. API availability
        if report.get('network_analysis', {}).get('api_patterns'):
            assessment['factors']['positive'].append('API endpoints available - more efficient')
            assessment['max_concurrent'] = max(assessment['max_concurrent'], 3)
            assessment['recommendations'].append('Use API endpoints for better performance')

        # 3. CDN usage (can handle more traffic)
        external_services = report.get('network_analysis', {}).get('external_services', {})
        if 'cdn' in external_services:
            assessment['factors']['positive'].append('CDN usage suggests good infrastructure')
            assessment['max_concurrent'] = max(assessment['max_concurrent'], 4)

        # 4. Fast response times
        if 0 < avg_response_time < 200:
            assessment['factors']['positive'].append(f'Fast server response ({avg_response_time:.0f}ms avg)')
            assessment['recommended_delay'] = 1

        # Calculate final risk level
        neg_count = len(assessment['factors']['negative'])
        pos_count = len(assessment['factors']['positive'])

        if neg_count >= 3 or 'Rate limiting detected' in assessment['factors']['negative']:
            assessment['risk_level'] = 'high'
            assessment['safe'] = False
        elif neg_count >= 2:
            assessment['risk_level'] = 'medium'
        elif pos_count >= 2 and neg_count <= 1:
            assessment['risk_level'] = 'low'

        # Final recommendations
        if assessment['risk_level'] == 'high':
            assessment['recommendations'].extend([
                'Start with single-threaded scraping',
                'Monitor for blocking or rate limits',
                'Consider using a scraping service or API'
            ])
        elif assessment['risk_level'] == 'medium':
            assessment['recommendations'].extend([
                f'Limit to {assessment["max_concurrent"]} concurrent requests',
                f'Use {assessment["recommended_delay"]}s delay between requests',
                'Implement exponential backoff on errors'
            ])
        else:
            assessment['recommendations'].extend([
                f'Safe to use up to {assessment["max_concurrent"]} concurrent requests',
                'Monitor response times and adjust accordingly'
            ])

        # Always recommend polite scraping
        assessment['recommendations'].append('Always respect robots.txt and terms of service')

        return assessment

    def _measure_tactic_impact(self, before_state: Dict) -> Dict:
        """Measure the comprehensive impact of a liberation tactic"""
        impact = {
            'success': True,
            'elements_changed': 0,
            'url_changed': False,
            'new_element_count': 0,
            'content_changes': {},
            'visibility_changes': {},
            'performance_impact': {},
            'significant_change': False,
            'error': None
        }

        try:
            # 1. Element count changes
            current_element_count = len(self.driver.find_elements(By.XPATH, '//*'))
            impact['new_element_count'] = current_element_count
            impact['elements_changed'] = abs(current_element_count - before_state.get('element_count', 0))

            # 2. URL changes
            current_url = self.driver.current_url
            impact['url_changed'] = current_url != before_state.get('url', '')
            if impact['url_changed']:
                impact['new_url'] = current_url

            # 3. Content changes (more meaningful than just count)
            current_body_text = self.driver.find_element(By.TAG_NAME, 'body').text
            current_text_length = len(current_body_text)
            before_text_length = before_state.get('body_length', 0)

            impact['content_changes'] = {
                'text_length_before': before_text_length,
                'text_length_after': current_text_length,
                'text_added': max(0, current_text_length - before_text_length),
                'text_removed': max(0, before_text_length - current_text_length),
                'percent_change': abs(current_text_length - before_text_length) / max(before_text_length, 1) * 100
            }

            # 4. Visibility changes - what became visible?
            visibility_check = self.driver.execute_script("""
                return {
                    visible_elements: document.querySelectorAll(':not([style*="display: none"]):not([hidden])').length,
                    hidden_elements: document.querySelectorAll('[style*="display: none"], [hidden]').length,
                    viewport_height: window.innerHeight,
                    document_height: document.documentElement.scrollHeight,
                    scrollable: document.documentElement.scrollHeight > window.innerHeight
                };
            """)

            before_visible = before_state.get('visible_elements', 0)
            current_visible = visibility_check['visible_elements']

            impact['visibility_changes'] = {
                'elements_revealed': max(0, current_visible - before_visible),
                'elements_hidden': max(0, before_visible - current_visible),
                'hidden_count': visibility_check['hidden_elements'],
                'page_height_change': visibility_check['document_height'] - before_state.get('document_height', 0),
                'became_scrollable': visibility_check['scrollable'] and not before_state.get('scrollable', False)
            }

            # 5. Specific liberation indicators
            liberation_check = self.driver.execute_script("""
                return {
                    // Paywall/overlay removal indicators
                    no_fixed_overlays: document.querySelectorAll('div[style*="position: fixed"][style*="top: 0"][style*="left: 0"]').length === 0,
                    no_blur: document.querySelectorAll('[style*="blur"]').length === 0,

                    // Content accessibility
                    text_selectable: document.body.style.userSelect !== 'none',
                    right_click_enabled: document.oncontextmenu === null,

                    // New interactive elements
                    new_buttons: document.querySelectorAll('button:not([data-seen])').length,
                    new_links: document.querySelectorAll('a[href]:not([data-seen])').length,
                    new_inputs: document.querySelectorAll('input:not([data-seen])').length
                };
            """)

            impact['liberation_indicators'] = liberation_check

            # 6. Performance impact
            timing_check = self.driver.execute_script("""
                const now = performance.now();
                return {
                    time_since_navigation: now,
                    dom_content_loaded: performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart,
                    resources_loaded: performance.getEntriesByType('resource').length
                };
            """)

            impact['performance_impact'] = {
                'execution_time': timing_check['time_since_navigation'] - before_state.get('timestamp', 0),
                'resource_change': timing_check['resources_loaded'] - before_state.get('resources_loaded', 0)
            }

            # 7. Determine if change is significant
            significant_factors = [
                impact['elements_changed'] > 10,
                impact['content_changes']['percent_change'] > 10,
                impact['visibility_changes']['elements_revealed'] > 5,
                impact['url_changed'],
                liberation_check['no_fixed_overlays'] and not before_state.get('no_fixed_overlays', True),
                liberation_check['no_blur'] and not before_state.get('no_blur', True),
                liberation_check['new_buttons'] > 0 or liberation_check['new_links'] > 0
            ]

            impact['significant_change'] = any(significant_factors)

            # 8. Generate human-readable summary
            summary = []
            if impact['elements_changed'] > 0:
                summary.append(f"{impact['elements_changed']} elements changed")
            if impact['visibility_changes']['elements_revealed'] > 0:
                summary.append(f"{impact['visibility_changes']['elements_revealed']} elements revealed")
            if impact['content_changes']['text_added'] > 100:
                summary.append(f"~{impact['content_changes']['text_added']} characters of text revealed")
            if liberation_check['no_fixed_overlays']:
                summary.append("Overlays removed")
            if liberation_check['no_blur']:
                summary.append("Blur effects removed")

            impact['summary'] = summary

        except Exception as e:
            self.logger.error(f"Error measuring tactic impact: {e}")
            impact['success'] = False
            impact['error'] = str(e)

            # Fallback to basic measurement
            try:
                current_element_count = len(self.driver.find_elements(By.XPATH, '//*'))
                impact['new_element_count'] = current_element_count
                impact['elements_changed'] = abs(current_element_count - before_state.get('element_count', 0))
                impact['url_changed'] = self.driver.current_url != before_state.get('url', '')
            except Exception as fallback_error:
                self.logger.error(f"Even fallback measurement failed: {fallback_error}")

        return impact

    def _analyze_captured_network(self) -> Dict:
        """Extract actionable network intelligence for scraper building"""
        network_analysis = {
            'total_requests': 0,
            'api_endpoints': [],  # Simple list of API URLs
            'auth_required': False,  # Simple yes/no
            'rate_limit_detected': False,
            'recommended_delay': 1.0  # Safe default
        }

        try:
            # Get network data (keep existing collection method)
            if hasattr(self, 'monitoring_active') and self.monitoring_active:
                network_data = self.driver.execute_script(
                    "return window.__reconMonitoring ? window.__reconMonitoring.network : [];"
                )

                network_analysis['total_requests'] = len(network_data)

                for request in network_data:
                    url = request.get('name', '')
                    if not url or url.startswith('data:'):
                        continue

                    # Simple API detection
                    if any(marker in url for marker in ['/api/', '/v1/', '/v2/', '.json']):
                        if url not in network_analysis['api_endpoints']:
                            network_analysis['api_endpoints'].append(url)

                    # Simple auth detection (just check the URL)
                    if any(term in url.lower() for term in ['auth', 'login', 'token']):
                        network_analysis['auth_required'] = True

            # Also check AJAX captures (if they exist)
            if hasattr(self, 'captured_data') and 'ajax_captures' in self.captured_data:
                for capture in self.captured_data.get('ajax_captures', []):
                    # Check for rate limiting (simple!)
                    if capture.get('status') == 429:
                        network_analysis['rate_limit_detected'] = True
                        network_analysis['recommended_delay'] = 2.0  # Be safe

            self.logger.info(f"[NETWORK] Found {len(network_analysis['api_endpoints'])} API endpoints")

        except Exception as e:
            self.logger.error(f"[NETWORK] Error: {e}")

        return network_analysis

    def _analyze_path_patterns(self) -> Dict[str, Any]:
        """Extract URL patterns for direct access"""
        patterns = {
            'url_depth': 0,
            'id_examples': [],  # Just collect examples
            'common_paths': []  # Most frequent paths
        }

        try:
            # Get all internal links
            paths = self.driver.execute_script("""
                const paths = [];
                document.querySelectorAll('a[href]').forEach(a => {
                    try {
                        const url = new URL(a.href);
                        if (url.origin === window.location.origin) {
                            paths.push(url.pathname);
                        }
                    } catch(e) {}
                });
                return paths;
            """)

            # Simple analysis
            path_counts = {}

            for path in paths:
                # Count frequency
                path_counts[path] = path_counts.get(path, 0) + 1

                # Check depth
                depth = len([s for s in path.split('/') if s])
                patterns['url_depth'] = max(patterns['url_depth'], depth)

                # Collect ID examples (simple patterns only)
                segments = path.split('/')
                for segment in segments:
                    if segment.isdigit() and segment not in patterns['id_examples']:
                        patterns['id_examples'].append(segment)
                        if len(patterns['id_examples']) >= 5:  # Limit examples
                            break

            # Get most common paths
            patterns['common_paths'] = sorted(
                path_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]  # Top 10

            # Simplify output
            patterns['common_paths'] = [path for path, count in patterns['common_paths']]

        except Exception as e:
            self.logger.debug(f"Path analysis error: {e}")

        return patterns

    def _probe_single_download(self, url: str) -> Dict:
        """Test if a download URL is accessible"""
        probe_script = """
        async function probeDownload(url) {
            try {
                const response = await fetch(url, {
                    method: 'HEAD',
                    mode: 'cors',
                    credentials: 'same-origin'
                });

                return {
                    url: url,
                    accessible: response.ok,
                    status: response.status,
                    content_type: response.headers.get('content-type'),
                    content_length: response.headers.get('content-length')
                };
            } catch (error) {
                return {
                    url: url,
                    accessible: false,
                    error: error.message
                };
            }
        }
        return probeDownload(arguments[0]);
        """

        try:
            return self.driver.execute_script(probe_script, url)
        except:
            return {'url': url, 'accessible': False, 'error': 'Script failed'}

    def _find_downloadable_files(self) -> Dict:
        """Find and test downloadable files on the page"""
        results = {
            'download_links': [],
            'accessible': [],
            'blocked': []
        }

        # Find download links
        find_script = """
        const links = [];
        const downloadExtensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.csv', '.txt', '.zip'];

        document.querySelectorAll('a[href]').forEach(link => {
            const href = link.href;
            // Check for file extensions OR download attribute
            if (downloadExtensions.some(ext => href.toLowerCase().includes(ext)) || 
                link.hasAttribute('download')) {
                links.push({
                    url: href,
                    text: link.textContent.trim(),
                    type: 'direct_link'
                });
            }
        });

        return links;
        """

        try:
            links = self.driver.execute_script(find_script)
            results['download_links'] = links

            # Test accessibility (limit to prevent detection)
            for link in links[:5]:  # Test first 5
                probe_result = self._probe_single_download(link['url'])

                if probe_result['accessible']:
                    results['accessible'].append(probe_result)
                else:
                    results['blocked'].append(probe_result)

        except Exception as e:
            self.logger.debug(f"Download detection error: {e}")

        return results

    def _get_recent_network(self) -> List[Dict]:
        """Get recent network activity"""
        try:
            return self.driver.execute_script("""
                if (window.__reconMonitoring && window.__reconMonitoring.network) {
                    // Get last 10 requests (simpler, less data)
                    return window.__reconMonitoring.network.slice(-10).map(req => ({
                        url: req.name || '',
                        type: req.type || 'unknown',
                        duration: req.duration || 0
                    }));
                }
                return [];
            """)
        except:
            return []

    def _extract_url_patterns(self) -> List[str]:
        """Extract common URL patterns"""
        try:
            # Get unique paths only (simpler approach)
            paths = self.driver.execute_script("""
                const paths = new Set();
                document.querySelectorAll('a[href]').forEach(a => {
                    try {
                        const url = new URL(a.href);
                        if (url.origin === window.location.origin) {
                            paths.add(url.pathname);
                        }
                    } catch(e) {}
                });
                return Array.from(paths);
            """)

            # Return as-is, let the analyzer decide on patterns
            return paths[:50]  # Reasonable limit

        except Exception as e:
            self.logger.debug(f"URL extraction error: {e}")
            return []

    # ////

    def _calculate_impact(self, before: Dict, after: Dict, context: Optional[Dict] = None) -> Dict:
        """Calculate comprehensive impact of any action/tactic"""

        # Basic change metrics
        impact = {
            'url_changed': before.get('url', '') != after.get('url', ''),
            'elements_added': after.get('element_count', 0) - before.get('element_count', 0),
            'text_added': after.get('body_length', 0) - before.get('body_length', 0),
            'cookies_modified': after.get('cookies', 0) != before.get('cookies', 0),
            'storage_modified': after.get('local_storage_items', 0) != before.get('local_storage_items', 0),
        }

        # Content accessibility metrics
        if before.get('body_length', 0) > 0:
            impact['content_increase_pct'] = ((after.get('body_length', 0) - before.get('body_length', 0))
                                              / before.get('body_length', 0)) * 100
        else:
            impact['content_increase_pct'] = 0

        # Feature accessibility changes
        impact['features_unlocked'] = []

        # Check what became accessible
        if after.get('downloadable_content', 0) > before.get('downloadable_content', 0):
            impact['features_unlocked'].append('additional_downloads')

        if after.get('interactive_elements', 0) > before.get('interactive_elements', 0):
            impact['features_unlocked'].append('new_interactions')

        if before.get('has_overlays', True) and not after.get('has_overlays', False):
            impact['features_unlocked'].append('unobstructed_view')

        # Overall effectiveness rating
        significant_changes = (
                impact['url_changed'] or
                abs(impact['elements_added']) > 10 or
                abs(impact['text_added']) > 100 or
                len(impact['features_unlocked']) > 0 or
                impact['content_increase_pct'] > 20
        )

        # Rate the impact
        if significant_changes and len(impact['features_unlocked']) > 0:
            impact['effectiveness'] = 'high'
        elif significant_changes or impact['content_increase_pct'] > 10:
            impact['effectiveness'] = 'medium'
        else:
            impact['effectiveness'] = 'low'

        # Add context if provided (e.g., tactic name, method used)
        if context:
            impact['context'] = context

        return impact

    def _calculate_scraping_complexity(self, report: Dict) -> Dict:
        """Calculate detailed complexity assessment for scraping approach"""

        # Start with base assessment
        assessment = {
            'score': 2,  # Base complexity
            'factors': [],
            'challenges': [],
            'recommended_approach': 'static_parsing'
        }

        # Factor analysis with explanations
        complexity_factors = {
            'javascript_required': {
                'weight': 2,
                'challenge': 'Dynamic content rendering',
                'approach_change': 'browser_automation'
            },
            'authentication_required': {
                'weight': 3,
                'challenge': 'Session management needed',
                'approach_change': 'authenticated_scraping'
            },
            'rate_limits_detected': {
                'weight': 1,
                'challenge': 'Request throttling required',
                'approach_change': None  # Doesn't change approach
            },
            'anti_bot_measures': {
                'weight': 3,
                'challenge': 'Bot detection countermeasures',
                'approach_change': 'advanced_automation'
            },
            'complex_pagination': {
                'weight': 2,
                'challenge': 'Multi-step navigation required',
                'approach_change': 'stateful_scraping'
            },
            'api_available': {
                'weight': -2,  # Reduces complexity!
                'challenge': None,
                'approach_change': 'api_integration'
            }
        }

        # Evaluate each factor
        features = report.get('discovered_features', {})
        network = report.get('network_analysis', {})

        # JavaScript requirement
        if features.get('uses_javascript'):
            assessment['score'] += complexity_factors['javascript_required']['weight']
            assessment['factors'].append('javascript_required')
            assessment['challenges'].append(complexity_factors['javascript_required']['challenge'])
            assessment['recommended_approach'] = 'browser_automation'

        # Authentication
        if features.get('has_login') or network.get('auth_required'):
            assessment['score'] += complexity_factors['authentication_required']['weight']
            assessment['factors'].append('authentication_required')
            assessment['challenges'].append(complexity_factors['authentication_required']['challenge'])

        # Rate limiting
        if network.get('rate_limit_detected'):
            assessment['score'] += complexity_factors['rate_limits_detected']['weight']
            assessment['factors'].append('rate_limits_detected')
            assessment['challenges'].append(complexity_factors['rate_limits_detected']['challenge'])

        # Anti-bot measures
        if len(report.get('access_barriers', [])) > 2:
            assessment['score'] += complexity_factors['anti_bot_measures']['weight']
            assessment['factors'].append('anti_bot_measures')
            assessment['challenges'].append(complexity_factors['anti_bot_measures']['challenge'])
            assessment['recommended_approach'] = 'advanced_automation'

        # Pagination complexity
        if report.get('pagination_patterns', {}).get('style') == 'infinite':
            assessment['score'] += complexity_factors['complex_pagination']['weight']
            assessment['factors'].append('complex_pagination')
            assessment['challenges'].append(complexity_factors['complex_pagination']['challenge'])

        # API availability (reduces complexity!)
        if network.get('api_endpoints', []):
            assessment['score'] += complexity_factors['api_available']['weight']
            assessment['factors'].append('api_available')
            assessment['recommended_approach'] = 'api_integration'

        # Normalize score
        assessment['score'] = max(1, min(10, assessment['score']))

        # Add human-readable summary
        if assessment['score'] <= 3:
            assessment['difficulty'] = 'simple'
            assessment['time_estimate'] = '1-2 hours'
        elif assessment['score'] <= 6:
            assessment['difficulty'] = 'moderate'
            assessment['time_estimate'] = '4-8 hours'
        else:
            assessment['difficulty'] = 'complex'
            assessment['time_estimate'] = '1-3 days'

        return assessment

    def _analyze_tactic_effectiveness(self, results: List[Dict]) -> Dict:
        """Analyze effectiveness across multiple tactics"""

        analysis = {
            'total_tactics': len(results),
            'successful_tactics': 0,
            'high_impact_tactics': [],
            'failed_tactics': [],
            'most_effective': None,
            'recommendations': []
        }

        # Analyze each result
        for result in results:
            if result.get('success'):
                analysis['successful_tactics'] += 1

                # Check impact level
                if result.get('impact', {}).get('effectiveness') == 'high':
                    analysis['high_impact_tactics'].append({
                        'name': result.get('tactic'),
                        'impact': result.get('impact', {}).get('features_unlocked', [])
                    })
            else:
                analysis['failed_tactics'].append(result.get('tactic'))

        # Find most effective
        if analysis['high_impact_tactics']:
            analysis['most_effective'] = analysis['high_impact_tactics'][0]['name']

        # Generate recommendations
        if analysis['successful_tactics'] == 0:
            analysis['recommendations'].append("Consider more advanced techniques")
        elif analysis['high_impact_tactics']:
            analysis['recommendations'].append(f"Prioritize {analysis['most_effective']} for this site type")

        # Success rate
        if analysis['total_tactics'] > 0:
            analysis['success_rate'] = (analysis['successful_tactics'] / analysis['total_tactics']) * 100
        else:
            analysis['success_rate'] = 0

        return analysis

    def _estimate_reliability(self, report: Dict) -> Dict:
        """Comprehensive reliability assessment for data extraction"""

        assessment = {
            'score': 1.0,  # Start optimistic
            'confidence': 'high',
            'risk_factors': [],
            'stability_factors': [],
            'recommendations': []
        }

        # Risk factors that reduce reliability
        risk_weights = {
            'dynamic_javascript': {
                'weight': 0.15,
                'reason': 'Content may change between page loads',
                'mitigation': 'Use consistent wait strategies'
            },
            'anti_bot_protection': {
                'weight': 0.25,
                'reason': 'Active countermeasures detected',
                'mitigation': 'Implement rotation and humanization'
            },
            'rate_limiting': {
                'weight': 0.10,
                'reason': 'Request throttling may interrupt flow',
                'mitigation': 'Implement adaptive delays'
            },
            'authentication_required': {
                'weight': 0.15,
                'reason': 'Session management complexity',
                'mitigation': 'Robust session handling required'
            },
            'frequent_layout_changes': {
                'weight': 0.20,
                'reason': 'Site structure may change',
                'mitigation': 'Use flexible selectors'
            }
        }

        # Stability factors that increase reliability
        stability_bonuses = {
            'api_available': {
                'weight': 0.20,
                'reason': 'Direct data access is more stable',
                'benefit': 'Structured data format'
            },
            'consistent_url_patterns': {
                'weight': 0.10,
                'reason': 'Predictable navigation',
                'benefit': 'Direct access to resources'
            },
            'static_content': {
                'weight': 0.15,
                'reason': 'Content less likely to change',
                'benefit': 'Simple extraction methods work'
            }
        }

        # Evaluate risk factors
        features = report.get('discovered_features', {})
        network = report.get('network_analysis', {})

        # Dynamic content
        if features.get('uses_javascript'):
            assessment['score'] -= risk_weights['dynamic_javascript']['weight']
            assessment['risk_factors'].append({
                'factor': 'dynamic_javascript',
                'impact': risk_weights['dynamic_javascript']['weight'],
                'reason': risk_weights['dynamic_javascript']['reason'],
                'mitigation': risk_weights['dynamic_javascript']['mitigation']
            })

        # Anti-bot measures
        barriers = report.get('access_barriers', [])
        if any('cloudflare' in str(b).lower() for b in barriers) or len(barriers) > 2:
            assessment['score'] -= risk_weights['anti_bot_protection']['weight']
            assessment['risk_factors'].append({
                'factor': 'anti_bot_protection',
                'impact': risk_weights['anti_bot_protection']['weight'],
                'reason': risk_weights['anti_bot_protection']['reason'],
                'mitigation': risk_weights['anti_bot_protection']['mitigation']
            })

        # Rate limiting
        if network.get('rate_limit_detected'):
            assessment['score'] -= risk_weights['rate_limiting']['weight']
            assessment['risk_factors'].append({
                'factor': 'rate_limiting',
                'impact': risk_weights['rate_limiting']['weight'],
                'reason': risk_weights['rate_limiting']['reason'],
                'mitigation': risk_weights['rate_limiting']['mitigation']
            })

        # Authentication
        if features.get('has_login') or network.get('auth_required'):
            assessment['score'] -= risk_weights['authentication_required']['weight']
            assessment['risk_factors'].append({
                'factor': 'authentication_required',
                'impact': risk_weights['authentication_required']['weight'],
                'reason': risk_weights['authentication_required']['reason'],
                'mitigation': risk_weights['authentication_required']['mitigation']
            })

        # Check tactic success rate (indicates site difficulty)
        if 'tactic_results' in report:
            results = report['tactic_results']
            failed_count = sum(1 for r in results if not r.get('success'))
            if failed_count > 2:
                assessment['score'] -= 0.10
                assessment['risk_factors'].append({
                    'factor': 'resistance_to_techniques',
                    'impact': 0.10,
                    'reason': f'{failed_count} extraction techniques failed',
                    'mitigation': 'May require custom approach'
                })

        # Evaluate stability factors
        if network.get('api_endpoints'):
            assessment['score'] += stability_bonuses['api_available']['weight']
            assessment['stability_factors'].append({
                'factor': 'api_available',
                'benefit': stability_bonuses['api_available']['benefit'],
                'improvement': stability_bonuses['api_available']['weight']
            })

        if report.get('url_patterns', {}).get('consistent'):
            assessment['score'] += stability_bonuses['consistent_url_patterns']['weight']
            assessment['stability_factors'].append({
                'factor': 'consistent_url_patterns',
                'benefit': stability_bonuses['consistent_url_patterns']['benefit'],
                'improvement': stability_bonuses['consistent_url_patterns']['weight']
            })

        if not features.get('uses_javascript'):
            assessment['score'] += stability_bonuses['static_content']['weight']
            assessment['stability_factors'].append({
                'factor': 'static_content',
                'benefit': stability_bonuses['static_content']['benefit'],
                'improvement': stability_bonuses['static_content']['weight']
            })

        # Normalize and categorize
        assessment['score'] = max(0.1, min(1.0, assessment['score']))

        if assessment['score'] >= 0.8:
            assessment['confidence'] = 'high'
            assessment['recommendations'].append('Standard extraction methods should work reliably')
        elif assessment['score'] >= 0.6:
            assessment['confidence'] = 'medium'
            assessment['recommendations'].append('Implement error handling and retry logic')
            assessment['recommendations'].append('Monitor for changes in site structure')
        else:
            assessment['confidence'] = 'low'
            assessment['recommendations'].append('Consider alternative data sources')
            assessment['recommendations'].append('Implement robust monitoring and alerting')
            assessment['recommendations'].append('Plan for frequent maintenance')

        return assessment

    def _determine_best_approach(self, report: Dict) -> Dict:
        """Determine optimal extraction approach with reasoning"""

        analysis = {
            'recommended_approach': None,
            'reasoning': [],
            'alternatives': [],
            'implementation_notes': [],
            'estimated_effort': None
        }

        # Decision tree with explanations
        features = report.get('discovered_features', {})
        network = report.get('network_analysis', {})

        # Priority 1: API if available
        if network.get('api_endpoints'):
            analysis['recommended_approach'] = 'api_integration'
            analysis['reasoning'].append('Direct API access available')
            analysis['reasoning'].append('Most efficient and reliable method')
            analysis['implementation_notes'].append('Map API endpoints and parameters')
            analysis['implementation_notes'].append('Implement proper authentication if required')
            analysis['estimated_effort'] = 'low'

            # Still note alternatives
            if features.get('uses_javascript'):
                analysis['alternatives'].append({
                    'approach': 'browser_automation',
                    'when_to_use': 'If API lacks required data'
                })

        # Priority 2: Static parsing if no JS
        elif not features.get('uses_javascript'):
            analysis['recommended_approach'] = 'static_parsing'
            analysis['reasoning'].append('No JavaScript required for content')
            analysis['reasoning'].append('Fastest and most resource-efficient')
            analysis['implementation_notes'].append('Use requests + BeautifulSoup')
            analysis['implementation_notes'].append('Focus on robust selector strategies')
            analysis['estimated_effort'] = 'low'

            # Note enhancement options
            if features.get('has_search'):
                analysis['alternatives'].append({
                    'approach': 'search_based_discovery',
                    'when_to_use': 'To find all available content'
                })

        # Priority 3: AJAX monitoring for dynamic sites
        elif report.get('ajax_patterns', {}).get('detected'):
            analysis['recommended_approach'] = 'ajax_monitoring'
            analysis['reasoning'].append('Dynamic content loaded via AJAX')
            analysis['reasoning'].append('Can intercept data at the source')
            analysis['implementation_notes'].append('Monitor network requests')
            analysis['implementation_notes'].append('Parse JSON/XML responses directly')
            analysis['estimated_effort'] = 'medium'

            analysis['alternatives'].append({
                'approach': 'browser_automation',
                'when_to_use': 'If AJAX patterns are too complex'
            })

        # Default: Full browser automation
        else:
            analysis['recommended_approach'] = 'browser_automation'
            analysis['reasoning'].append('Complex JavaScript rendering required')
            analysis['reasoning'].append('Most flexible approach')
            analysis['implementation_notes'].append('Use Selenium or Playwright')
            analysis['implementation_notes'].append('Implement proper wait strategies')
            analysis['estimated_effort'] = 'high'

            # Suggest optimization
            analysis['alternatives'].append({
                'approach': 'hybrid_approach',
                'when_to_use': 'Combine static parsing with selective automation'
            })

        # Add specific recommendations based on features
        if features.get('has_login'):
            analysis['implementation_notes'].append('Implement session management')

        if report.get('rate_limits_detected'):
            analysis['implementation_notes'].append('Include rate limiting logic')

        return analysis

    def _determine_extraction_method(self, report: Dict) -> Dict:
        """Determine data extraction method with detailed guidance"""

        extraction_plan = {
            'primary_method': None,
            'secondary_methods': [],
            'data_formats': [],
            'selectors_strategy': None,
            'complexity': 'simple'
        }

        features = report.get('discovered_features', {})
        network = report.get('network_analysis', {})

        # Determine primary method based on data availability
        if network.get('api_endpoints'):
            extraction_plan['primary_method'] = 'json_parsing'
            extraction_plan['data_formats'].append('json')
            extraction_plan['selectors_strategy'] = 'json_paths'
            extraction_plan['complexity'] = 'simple'

        elif features.get('table_count', 0) > 0:
            extraction_plan['primary_method'] = 'table_extraction'
            extraction_plan['data_formats'].append('tabular')
            extraction_plan['selectors_strategy'] = 'table_specific'
            extraction_plan['complexity'] = 'simple'

            # Tables often have additional data
            extraction_plan['secondary_methods'].append('metadata_extraction')

        elif features.get('structured_data'):
            extraction_plan['primary_method'] = 'structured_data_extraction'
            extraction_plan['data_formats'].extend(['json-ld', 'microdata'])
            extraction_plan['selectors_strategy'] = 'semantic_selectors'
            extraction_plan['complexity'] = 'medium'

        elif features.get('form_count', 0) > 3:
            extraction_plan['primary_method'] = 'form_interaction'
            extraction_plan['data_formats'].append('form_responses')
            extraction_plan['selectors_strategy'] = 'form_based_navigation'
            extraction_plan['complexity'] = 'complex'
            extraction_plan['secondary_methods'].append('result_parsing')

        else:
            extraction_plan['primary_method'] = 'css_selectors'
            extraction_plan['data_formats'].append('html')
            extraction_plan['selectors_strategy'] = 'hierarchical_selectors'
            extraction_plan['complexity'] = 'medium'

        # Add robustness recommendations
        if extraction_plan['complexity'] != 'simple':
            extraction_plan['robustness_tips'] = [
                'Use multiple selector strategies',
                'Implement fallback selectors',
                'Validate extracted data',
                'Handle missing elements gracefully'
            ]

        return extraction_plan

    def _determine_session_needs(self, report: Dict) -> Dict:
        """Comprehensive session management requirements"""

        session_config = {
            'authentication': {
                'required': False,
                'method': None,
                'complexity': 'none'
            },
            'cookies': {
                'required': False,
                'persistent': False,
                'specific_cookies': []
            },
            'headers': {
                'required': ['User-Agent'],  # Always recommended
                'recommended': ['Referer', 'Accept-Language'],
                'custom': []
            },
            'state_management': {
                'required': False,
                'type': None
            },
            'implementation_guide': []
        }

        features = report.get('discovered_features', {})
        network = report.get('network_analysis', {})

        # Authentication analysis
        if features.get('has_login') or network.get('auth_required'):
            session_config['authentication']['required'] = True
            session_config['cookies']['required'] = True
            session_config['cookies']['persistent'] = True
            session_config['state_management']['required'] = True

            # Determine auth complexity
            if network.get('oauth_detected'):
                session_config['authentication']['method'] = 'oauth'
                session_config['authentication']['complexity'] = 'complex'
                session_config['implementation_guide'].append('Implement OAuth flow')
            elif network.get('token_endpoints'):
                session_config['authentication']['method'] = 'token'
                session_config['authentication']['complexity'] = 'medium'
                session_config['implementation_guide'].append('Implement token refresh logic')
            else:
                session_config['authentication']['method'] = 'cookie'
                session_config['authentication']['complexity'] = 'simple'
                session_config['implementation_guide'].append('Maintain cookie jar across requests')

        # Header requirements based on detected protection
        if report.get('access_barriers'):
            session_config['headers']['required'].extend(['Referer', 'Accept'])
            session_config['implementation_guide'].append('Mimic browser headers exactly')

        # State management for complex sites
        if features.get('uses_javascript') or report.get('spa_detected'):
            session_config['state_management']['type'] = 'browser_state'
            session_config['implementation_guide'].append('Maintain browser instance for session')
        elif session_config['cookies']['required']:
            session_config['state_management']['type'] = 'cookie_jar'
            session_config['implementation_guide'].append('Use persistent cookie storage')

        # Add best practices
        if session_config['authentication']['required']:
            session_config['best_practices'] = [
                'Store credentials securely',
                'Implement session timeout handling',
                'Add retry logic for auth failures',
                'Monitor for session expiration'
            ]

        return session_config

    # ////

    def _setup_comprehensive_monitoring(self):
        """Install targeted monitoring for scraper intelligence gathering"""

        # Focused monitoring script - only what helps build scrapers
        monitoring_script = """
        // Initialize monitoring with only essential data
        window.__reconMonitoring = {
            network: [],
            domChanges: [],
            ajaxPatterns: [],
            errors: []  // Keep minimal error tracking
        };

        // 1. NETWORK MONITORING - Essential for finding APIs
        const observer = new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
                // Only track actual data requests, not assets
                if (entry.name.includes('.css') || 
                    entry.name.includes('.jpg') || 
                    entry.name.includes('.png') || 
                    entry.name.includes('.woff')) {
                    continue;  // Skip static assets
                }

                window.__reconMonitoring.network.push({
                    url: entry.name,
                    type: entry.initiatorType || 'unknown',
                    duration: entry.duration,
                    size: entry.transferSize || 0,
                    timestamp: entry.startTime
                });
            }
        });

        try {
            observer.observe({ entryTypes: ['resource', 'xmlhttprequest', 'fetch'] });
        } catch(e) {
            observer.observe({ entryTypes: ['resource'] });
        }

        // 2. DOM CHANGE MONITORING - Essential for dynamic content detection
        let changeCount = 0;
        const domObserver = new MutationObserver((mutations) => {
            // Batch mutations to avoid overwhelming data
            changeCount += mutations.length;

            // Sample every 10th change to reduce data
            if (changeCount % 10 === 0) {
                window.__reconMonitoring.domChanges.push({
                    changeCount: changeCount,
                    timestamp: Date.now(),
                    // Just track that changes happened, not every detail
                    sample: mutations[0] ? {
                        type: mutations[0].type,
                        target: mutations[0].target.tagName
                    } : null
                });
            }
        });

        // Start DOM observation when ready
        if (document.body) {
            domObserver.observe(document.body, {
                childList: true,
                subtree: true
                // Removed attributes monitoring - too noisy
            });
        } else {
            document.addEventListener('DOMContentLoaded', () => {
                domObserver.observe(document.body, {
                    childList: true,
                    subtree: true
                });
            });
        }

        // 3. AJAX PATTERN DETECTION - Simplified from toolkit
        const originalFetch = window.fetch;
        window.fetch = function(...args) {
            const [url] = args;
            window.__reconMonitoring.ajaxPatterns.push({
                url: url,
                method: args[1]?.method || 'GET',
                timestamp: Date.now()
            });
            return originalFetch.apply(this, args);
        };

        // 4. CRITICAL ERROR MONITORING - Only major failures
        window.addEventListener('error', (event) => {
            // Only track errors that might affect scraping
            if (event.message.includes('fetch') || 
                event.message.includes('Failed') ||
                event.message.includes('blocked')) {
                window.__reconMonitoring.errors.push({
                    message: event.message,
                    timestamp: Date.now()
                });
            }
        });

        return true;
        """

        try:
            self.driver.execute_script(monitoring_script)
            self.logger.info("[MONITORING] Essential monitoring activated")
            self.monitoring_active = True

        except Exception as e:
            self.logger.warning(f"[MONITORING] Setup failed: {e}")
            self.monitoring_active = False

    def _catalog_site_features(self) -> Dict:
        """Comprehensive feature detection for extraction strategy"""

        features = {
            # Basic features
            'core': {
                'uses_javascript': False,
                'total_elements': 0,
                'page_size_kb': 0
            },

            # Interaction points
            'interactions': {
                'has_search': False,
                'has_login': False,
                'form_count': 0,
                'input_types': []
            },

            # Data presentation
            'data_structures': {
                'table_count': 0,
                'list_count': 0,
                'grid_detected': False,
                'iframe_count': 0
            },

            # Navigation
            'navigation': {
                'has_pagination': False,
                'pagination_type': None,
                'has_infinite_scroll': False,
                'menu_type': None
            },

            # Content types
            'content': {
                'has_downloads': False,
                'media_types': [],
                'structured_data': False
            }
        }

        try:
            # Enhanced feature detection
            detection_script = """
            const analysis = {
                core: {},
                interactions: {},
                data_structures: {},
                navigation: {},
                content: {}
            };

            // Core features
            analysis.core.uses_javascript = document.scripts.length > 0;
            analysis.core.total_elements = document.querySelectorAll('*').length;
            analysis.core.page_size_kb = Math.round(
                new Blob([document.documentElement.outerHTML]).size / 1024
            );

            // Interaction detection
            analysis.interactions.has_search = document.querySelectorAll(
                'input[type="search"], input[name*="search"], ' +
                'input[placeholder*="search" i], form[action*="search"]'
            ).length > 0;

            analysis.interactions.has_login = document.querySelectorAll(
                'input[type="password"], form[action*="login"], ' +
                'a[href*="login"], button:contains("Sign in")'
            ).length > 0;

            analysis.interactions.form_count = document.forms.length;

            // Get unique input types
            const inputTypes = new Set();
            document.querySelectorAll('input').forEach(input => {
                inputTypes.add(input.type || 'text');
            });
            analysis.interactions.input_types = Array.from(inputTypes);

            // Data structures
            analysis.data_structures.table_count = document.querySelectorAll('table').length;
            analysis.data_structures.list_count = 
                document.querySelectorAll('ul, ol').length;
            analysis.data_structures.grid_detected = 
                document.querySelectorAll('[class*="grid"], .row .col').length > 0;
            analysis.data_structures.iframe_count = document.querySelectorAll('iframe').length;

            // Navigation patterns
            const paginationSelectors = document.querySelectorAll(
                '.pagination, .pager, [class*="page"], ' +
                'a[href*="page="], a[href*="offset="]'
            );
            analysis.navigation.has_pagination = paginationSelectors.length > 0;

            // Detect pagination type
            if (analysis.navigation.has_pagination) {
                if (document.querySelector('.pagination li')) {
                    analysis.navigation.pagination_type = 'numbered';
                } else if (document.querySelector('[class*="next"], [class*="load-more"]')) {
                    analysis.navigation.pagination_type = 'next_prev';
                }
            }

            // Check for infinite scroll indicators
            analysis.navigation.has_infinite_scroll = 
                document.querySelector('[class*="infinite"], [data-infinite]') !== null ||
                window.IntersectionObserver !== undefined;

            // Content types
            analysis.content.has_downloads = document.querySelectorAll(
                'a[href$=".pdf"], a[href$=".doc"], a[href$=".csv"], ' +
                'a[href$=".xlsx"], a[download]'
            ).length > 0;

            // Detect media types
            const mediaTypes = new Set();
            if (document.querySelector('img')) mediaTypes.add('images');
            if (document.querySelector('video')) mediaTypes.add('video');
            if (document.querySelector('audio')) mediaTypes.add('audio');
            if (document.querySelector('canvas')) mediaTypes.add('canvas');
            analysis.content.media_types = Array.from(mediaTypes);

            // Check for structured data
            analysis.content.structured_data = 
                document.querySelector('script[type="application/ld+json"]') !== null ||
                document.querySelector('[itemscope]') !== null;

            return analysis;
            """

            features = self.driver.execute_script(detection_script)

            # Add intelligent insights based on features
            features['insights'] = self._generate_feature_insights(features)

        except Exception as e:
            self.logger.error(f"Feature detection error: {e}")

        return features

    def _generate_feature_insights(self, features: Dict) -> Dict:
        """Generate actionable insights from detected features"""

        insights = {
            'complexity': 'simple',
            'recommended_tools': [],
            'potential_challenges': [],
            'extraction_hints': []
        }

        # Assess complexity
        complexity_score = 0

        if features['core']['uses_javascript']:
            complexity_score += 2
            insights['recommended_tools'].append('selenium')
            insights['potential_challenges'].append('Dynamic content rendering')
        else:
            insights['recommended_tools'].append('requests + beautifulsoup')

        if features['interactions']['has_login']:
            complexity_score += 3
            insights['potential_challenges'].append('Authentication required')
            insights['extraction_hints'].append('Implement session management')

        if features['navigation']['has_infinite_scroll']:
            complexity_score += 2
            insights['potential_challenges'].append('Infinite scroll pagination')
            insights['extraction_hints'].append('Implement scroll automation')

        if features['data_structures']['iframe_count'] > 0:
            complexity_score += 1
            insights['potential_challenges'].append('Content in iframes')
            insights['extraction_hints'].append('Switch to iframe context')

        # Determine overall complexity
        if complexity_score <= 2:
            insights['complexity'] = 'simple'
        elif complexity_score <= 5:
            insights['complexity'] = 'moderate'
        else:
            insights['complexity'] = 'complex'

        # Add data format recommendations
        if features['data_structures']['table_count'] > 0:
            insights['extraction_hints'].append('Use pandas for table extraction')

        if features['content']['structured_data']:
            insights['extraction_hints'].append('Extract JSON-LD for rich metadata')

        if features['content']['has_downloads']:
            insights['extraction_hints'].append('Implement download handling')

        return insights

    def _generate_markdown_report(self, report: Dict) -> str:
        """Generate clear, actionable report"""

        # Basic info
        md = f"""# Site Analysis Report

    **URL**: {report.get('url', 'Unknown')}  
    **Date**: {report.get('timestamp', 'Unknown')}  
    **Session**: {report.get('metadata', {}).get('analysis_id', 'Unknown')}

    ## Quick Summary

    """

        # Use data we ACTUALLY have
        features = report.get('discovered_features', {})

        # Simple feature list
        md += f"- **Uses JavaScript**: {features.get('uses_javascript', False)}\n"
        md += f"- **Has Login**: {features.get('has_login', False)}\n"
        md += f"- **Has Search**: {features.get('has_search', False)}\n"
        md += f"- **Total Elements**: {features.get('total_elements', 0)}\n"

        # Access barriers (if any)
        barriers = report.get('access_barriers', [])
        if barriers:
            md += f"\n## Access Barriers ({len(barriers)})\n"
            for barrier in barriers:
                md += f"- {barrier}\n"

        # Network findings (simplified)
        network = report.get('network_analysis', {})
        if network.get('api_endpoints'):
            md += f"\n## API Endpoints Found ({len(network['api_endpoints'])})\n"
            for endpoint in network['api_endpoints'][:5]:
                md += f"- `{endpoint}`\n"

        # Tactic results (simple success/fail)
        tactics = report.get('tactic_results', [])
        if tactics:
            successful = sum(1 for t in tactics if t.get('success'))
            md += f"\n## Extraction Methods Tested\n"
            md += f"- **Success Rate**: {successful}/{len(tactics)}\n"

        # Simple recommendations
        md += "\n## Recommended Approach\n"

        # Basic decision tree
        if network.get('api_endpoints'):
            md += "- Use API endpoints directly (most efficient)\n"
        elif not features.get('uses_javascript'):
            md += "- Use simple HTML parsing (requests + BeautifulSoup)\n"
        else:
            md += "- Use browser automation (Selenium)\n"

        if features.get('has_login'):
            md += "- Implement session management\n"

        if network.get('rate_limit_detected'):
            md += "- Add delays between requests (2+ seconds)\n"

        md += f"\n---\n*Analysis complete*\n"

        return md

    def _generate_scraper_config(self, report: Dict) -> Dict:
        """Generate simple, usable scraper configuration"""

        features = report.get('discovered_features', {})
        network = report.get('network_analysis', {})

        # Determine approach (simple logic)
        if network.get('api_endpoints'):
            approach = 'api'
            tool = 'requests'
        elif not features.get('uses_javascript'):
            approach = 'static'
            tool = 'requests + beautifulsoup'
        else:
            approach = 'browser'
            tool = 'selenium'

        config = {
            'target': {
                'url': report.get('url', ''),
                'analyzed_at': report.get('timestamp', '')
            },

            'approach': approach,
            'primary_tool': tool,

            'requirements': {
                'javascript': features.get('uses_javascript', False),
                'authentication': features.get('has_login', False),
                'rate_limiting': network.get('rate_limit_detected', False)
            },

            'discovered_resources': {
                'api_endpoints': network.get('api_endpoints', []),
                'forms': len(report.get('forms', {})),
                'downloads': len(report.get('downloadable_content', []))
            },

            'settings': {
                'delay_seconds': 2 if network.get('rate_limit_detected') else 1,
                'timeout': 30,
                'retries': 3
            }
        }

        # Add simple notes
        notes = []
        if features.get('has_login'):
            notes.append("Set up session cookies or login automation")
        if features.get('table_count', 0) > 0:
            notes.append("Use pandas for table extraction")
        if network.get('api_endpoints'):
            notes.append("Test API endpoints with Postman first")

        if notes:
            config['implementation_notes'] = notes

        return config

    def _generate_scraper_blueprint(self, report: Dict) -> Dict:
        """Generate blueprint for building the perfect scraper - WITH CONCRETE DISCOVERIES"""

        blueprint = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'target_url': report.get('url', ''),
                'complexity_score': self._calculate_scraping_complexity(report),
                'estimated_reliability': self._estimate_reliability(report),
                'recon_session_id': report.get('metadata', {}).get('session_id', 'unknown')
            },

            'architecture': {
                'recommended_approach': self._determine_best_approach(report),
                'required_technologies': self._identify_required_tech(report),
                'session_management': self._determine_session_needs(report),
                'concurrency_safe': self._assess_concurrency_safety(report)
            },

            'discovered_patterns': {
                # ADD ACTUAL DISCOVERIES!
                'forms_found': [
                    {
                        'action': form.get('action'),
                        'method': form.get('method'),
                        'inputs': form.get('inputs', [])
                    }
                    for form in report.get('forms', [])[:3]  # Top 3 forms
                ],
                'api_endpoints_discovered': report.get('api_endpoints', [])[:10],
                'downloadable_resources': [
                    {
                        'type': item.get('type'),
                        'url': item.get('url'),
                        'text': item.get('text', '')[:50]
                    }
                    for item in report.get('downloadable_content', [])[:5]
                ],
                'ajax_patterns': report.get('ajax_patterns', {}).get('patterns', {})
            },

            'entry_points': self._identify_entry_points(report),

            'data_extraction': {
                'primary_method': self._determine_extraction_method(report),
                'discovered_selectors': self._extract_actual_selectors(report),  # NEW!
                'sample_data_structures': self._extract_sample_data(report),  # NEW!
                'data_formats': self._identify_data_formats(report),
                'transformation_required': self._assess_transformation_needs(report)
            },

            'navigation_strategy': self._design_navigation_strategy(report),
            'pagination_approach': self._design_pagination_approach(report),
            'authentication_handling': self._design_auth_strategy(report),
            'rate_limiting_strategy': self._design_rate_limit_strategy(report),
            'error_handling': self._design_error_handling(report),
            'optimization_tips': self._generate_optimization_tips(report),

            'code_template': self._generate_code_template(report),
            'testing_strategy': self._design_testing_strategy(report),

            # NEW: Concrete next steps!
            'implementation_checklist': self._generate_implementation_checklist(report)
        }

        return blueprint

    def _generate_code_template(self, report: Dict) -> str:
        """Generate INTELLIGENT starter code using ACTUAL discoveries"""
        approach = self._determine_best_approach(report)

        # Extract actual discoveries to embed in template
        discovered_endpoints = report.get('api_endpoints', [])[:3]
        discovered_selectors = self._extract_actual_selectors(report)
        form_data = report.get('forms', [])

        if approach == 'api_first' and discovered_endpoints:
            # Use ACTUAL discovered endpoints!
            template = f'''import requests
    import json
    import time
    from typing import Dict, List

    class {self._generate_class_name(report)}Scraper:
        """Auto-generated scraper for {report.get('url', 'target site')}"""

        def __init__(self):
            self.session = requests.Session()
            self.base_url = "{report.get('url', '').rstrip('/')}"

            # Discovered endpoints from reconnaissance!
            self.api_endpoints = {{
                'main': {json.dumps(discovered_endpoints, indent=12)}
            }}

            # Headers discovered during recon
            self.headers = {{
                'User-Agent': 'Mozilla/5.0 (Research Bot)',
                'Accept': 'application/json'
            }}

        def fetch_data(self, endpoint: str, params: Dict = None) -> Dict:
            """Fetch data with discovered patterns"""
            url = endpoint if endpoint.startswith('http') else f"{{self.base_url}}{{endpoint}}"

            response = self.session.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            # Handle discovered response formats
            if 'json' in response.headers.get('content-type', ''):
                return response.json()
            return {{'raw': response.text}}

        def run(self):
            """Execute scraping with discovered patterns"""
            results = []

            for endpoint in self.api_endpoints['main']:
                try:
                    data = self.fetch_data(endpoint)
                    results.append(data)
                    print(f"✓ Fetched: {{endpoint}}")

                    # Rate limiting based on recon findings
                    time.sleep({report.get('rate_limits', {}).get('recommended_delay', 1)})

                except Exception as e:
                    print(f"✗ Failed {{endpoint}}: {{e}}")
                    continue

            return results
    '''

        elif approach == 'browser_automation':
            # Include ACTUAL selectors found!
            selector_section = self._format_selectors_for_code(discovered_selectors)

            template = f'''from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import time
    from typing import List, Dict

    class {self._generate_class_name(report)}Scraper:
        """Auto-generated Selenium scraper with discovered patterns"""

        def __init__(self):
            self.driver = webdriver.Chrome()
            self.base_url = "{report.get('url', '')}"
            self.wait = WebDriverWait(self.driver, 10)

            # Selectors discovered during reconnaissance!
            self.selectors = {{
    {selector_section}
            }}

        def navigate_to_page(self, url: str = None):
            """Navigate using discovered patterns"""
            target_url = url or self.base_url
            self.driver.get(target_url)

            # Wait for key element discovered during recon
            if 'main_content' in self.selectors:
                self.wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self.selectors['main_content'])
                ))

        def extract_data(self) -> List[Dict]:
            """Extract using discovered selectors"""
            data = []

            # Use actual discovered patterns!
            for key, selector in self.selectors.items():
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        data.append({{
                            'type': key,
                            'text': elem.text,
                            'href': elem.get_attribute('href') if elem.tag_name == 'a' else None
                        }})
                except Exception as e:
                    print(f"Failed to extract {{key}}: {{e}}")

            return data

        def handle_pagination(self):
            """Handle pagination based on discovered patterns"""
            pagination_type = '{report.get('pagination_patterns', {}).get('style', 'none')}'

            if pagination_type == 'numbered':
                # Implementation based on discoveries
                pass
            elif pagination_type == 'infinite':
                # Scroll-based implementation
                pass

        def run(self):
            """Execute with all discovered patterns"""
            try:
                self.navigate_to_page()

                # Apply liberation tactics if needed
                {self._generate_liberation_code(report)}

                data = self.extract_data()

                # Handle pagination if discovered
                if '{report.get('pagination_patterns', {}).get('has_pagination', False)}' == 'True':
                    self.handle_pagination()

                return data

            finally:
                self.driver.quit()
    '''

        else:  # static_html approach
            template = self._generate_static_template(report, discovered_selectors)

        return template

    def _extract_actual_selectors(self, report: Dict) -> Dict[str, str]:
        """Extract CSS selectors from actual page analysis"""
        selectors = {}

        # From discovered features
        if report.get('discovered_features', {}).get('has_search'):
            selectors['search_input'] = 'input[type="search"], input[name*="search"]'

        # From forms analysis
        for form in report.get('forms', []):
            if 'search' in str(form).lower():
                selectors['search_form'] = f'form[action="{form.get("action", "")}"]'

        # From downloadable content
        if report.get('downloadable_content'):
            selectors['download_links'] = 'a[href$=".pdf"], a[download]'

        # Add more based on actual discoveries...

        return selectors

    def _extract_sample_data(self, report: Dict) -> List[Dict]:
        """Extract sample data structures found during recon"""
        samples = []

        # From hidden data extraction
        if report.get('baseline', {}).get('metadata', {}).get('ldJson'):
            samples.append({
                'type': 'json-ld',
                'structure': report['baseline']['metadata']['ldJson'][:1]  # First item
            })

        # From AJAX captures
        for capture in report.get('captured_data', {}).get('ajax_captures', [])[:3]:
            if capture.get('response'):
                samples.append({
                    'type': 'api_response',
                    'endpoint': capture.get('url'),
                    'structure': capture.get('response')
                })

        return samples

    def _generate_class_name(self, report: Dict) -> str:
        """Generate appropriate class name from URL"""
        from urllib.parse import urlparse
        domain = urlparse(report.get('url', '')).netloc
        # Convert domain.com to DomainCom
        return ''.join(word.capitalize() for word in domain.replace('.', '_').split('_'))

    def _generate_optimization_tips(self, report: Dict) -> List[str]:
        """Generate SPECIFIC optimization tips based on ACTUAL findings"""
        tips = []

        # API optimization - with concrete details!
        api_endpoints = report.get('api_endpoints', [])
        if api_endpoints:
            tips.append(f"Use discovered API endpoints directly: {api_endpoints[0]}")
            if len(api_endpoints) > 3:
                tips.append(f"Found {len(api_endpoints)} endpoints - consider parallel requests")

        # Caching - be specific!
        if not report.get('discovered_features', {}).get('uses_javascript'):
            tips.append("Site is static HTML - aggressive caching will work well")

        # Rate limiting - use actual discoveries
        if report.get('network_summary', {}).get('avg_response_time', 0) < 200:
            tips.append("Server responds quickly (<200ms) - can increase request rate")

        # Data volume insights
        total_elements = report.get('discovered_features', {}).get('total_elements', 0)
        if total_elements > 1000:
            tips.append(f"Page has {total_elements} elements - use CSS selectors to target only needed data")

        # Form-specific tips
        if report.get('forms', {}).get('search_forms'):
            tips.append("Search form discovered - use it instead of crawling all pages")

        return tips

    def _generate_selectors(self, report: Dict) -> Dict:
        """Extract ACTUAL selectors from reconnaissance data"""
        selectors = {}

        # Extract from baseline DOM analysis
        baseline_dom = report.get('baseline', {}).get('dom', {})

        # Find actual title elements
        if baseline_dom:
            # Look for elements with substantial text that could be titles
            # This would need the DOM analysis to tag likely titles
            selectors['title'] = 'h1'  # Default, but we could be smarter

        # Extract from forms we found
        for form in report.get('forms', []):
            form_id = form.get('id')
            if form_id:
                selectors[f'form_{form_id}'] = f'#{form_id}'
            for input_field in form.get('inputs', []):
                if input_field.get('name'):
                    selectors[f'input_{input_field["name"]}'] = f'[name="{input_field["name"]}"]'

        # Extract from downloadable content patterns
        if report.get('downloadable_content'):
            # Build selector from actual found patterns
            download_extensions = set()
            for item in report['downloadable_content']:
                if item.get('extension'):
                    download_extensions.add(item['extension'])

            if download_extensions:
                selectors['downloads'] = ', '.join([f'a[href$="{ext}"]' for ext in download_extensions])

        # Tables found
        table_count = report.get('discovered_features', {}).get('table_count', 0)
        if table_count > 0:
            selectors['data_tables'] = 'table'  # Could be more specific with IDs/classes from DOM

        # Pagination from actual discoveries
        if report.get('pagination_patterns', {}).get('selector'):
            selectors['pagination'] = report['pagination_patterns']['selector']

        return selectors

    def _initialize_report(self, url: str, mode: str) -> Dict[str, Any]:
        """Initialize report structure - CLEAN, NO DUPLICATION"""

        session_id = self.session_id if hasattr(self, 'session_id') else datetime.now().strftime("%Y%m%d_%H%M%S")

        return {
            # Single source of truth for metadata
            'metadata': {
                'url': url,
                'mode': mode,
                'timestamp': datetime.now().isoformat(),
                'session_id': session_id,
                'analysis_id': f'recon_{session_id}',
                'title': '',  # Filled after page load
                'artifacts_path': str(self.base_path)  # Set immediately!
            },

            # Core discoveries - what we found
            'discoveries': {
                'features': {},  # was discovered_features
                'downloads': [],  # was downloadable_content
                'barriers': [],  # was access_barriers
                'forms': [],  # Keep forms as list for consistency
                'ajax': {},  # was ajax_patterns
                'api_endpoints': []
            },

            # Actions taken
            'liberation_results': [],

            # Raw captured data
            'captured_data': {
                'dom_snapshots': [],
                'network_log': [],
                'metadata_timeline': []
            },

            # Analysis results - what we learned
            'analysis': {
                'search_patterns': {},
                'pagination_patterns': {},
                'data_structures': {},
                'tech_stack': {},
                'url_patterns': {},
                'navigation_flows': {},
                'authentication': {},
                'rate_limits': {}
            },

            # Screenshots tracked in single place
            'artifacts': {
                'screenshots': [],
                'dom_snapshots': [],
                'network_logs': {}
            },

            # Baseline snapshot
            'baseline': {},

            # Final outputs
            'scraper_blueprint': {},
            'recommended_approach': []
        }

    # ////

    def _design_navigation_strategy(self, report: Dict) -> Dict:
        """Design navigation strategy using ACTUAL discoveries"""

        # Start with discovered capabilities
        has_search = len(report.get('forms', [])) > 0
        has_pagination = report.get('pagination_patterns', {}).get('has_pagination', False)
        api_available = len(report.get('api_endpoints', [])) > 0

        strategy = {
            # Can have MULTIPLE types!
            'capabilities': {
                'search': has_search,
                'pagination': has_pagination,
                'api_access': api_available
            },

            # Primary approach based on best option
            'primary_approach': self._determine_primary_navigation(has_search, has_pagination, api_available),

            # Actual discovered entry points
            'entry_points': self._extract_concrete_entry_points(report),

            # Practical guidance
            'implementation': self._get_navigation_implementation(report)
        }

        return strategy

    def _determine_primary_navigation(self, has_search: bool, has_pagination: bool, has_api: bool) -> str:
        """Determine best navigation approach"""
        if has_api:
            return 'api_direct'  # Best option!
        elif has_search:
            return 'search_driven'  # Second best
        elif has_pagination:
            return 'paginated_crawl'
        else:
            return 'single_page'  # Simplest

    def _extract_concrete_entry_points(self, report: Dict) -> List[Dict]:
        """Extract ACTUAL URLs and forms to use"""
        entry_points = []

        # Main URL
        entry_points.append({
            'url': report.get('metadata', {}).get('url', ''),
            'type': 'main'
        })

        # Actual search forms found
        for form in report.get('forms', []):
            if 'search' in str(form).lower():
                entry_points.append({
                    'url': form.get('action', ''),
                    'type': 'search_form',
                    'method': form.get('method', 'GET'),
                    'inputs': [inp['name'] for inp in form.get('inputs', []) if inp.get('name')]
                })

        # API endpoints discovered
        for endpoint in report.get('api_endpoints', [])[:3]:  # Top 3
            entry_points.append({
                'url': endpoint,
                'type': 'api'
            })

        return entry_points

    def _design_pagination_approach(self, report: Dict) -> Dict:
        """Design pagination approach with ACTUAL selectors"""
        pagination = report.get('pagination_patterns', {})

        if not pagination.get('has_pagination'):
            return {'enabled': False, 'reason': 'No pagination detected'}

        approach = {
            'enabled': True,
            'style': pagination.get('style', 'unknown'),
            'discovered_patterns': {}  # NEW: Actual patterns found!
        }

        # Use ACTUAL discovered selectors/patterns
        if approach['style'] == 'numbered':
            approach['implementation'] = {
                'type': 'url_parameter',
                'discovered_params': self._extract_pagination_params(report),  # NEW!
                'example_urls': pagination.get('example_urls', [])  # NEW!
            }

        elif approach['style'] == 'load_more':
            approach['implementation'] = {
                'type': 'button_click',
                'selector': pagination.get('selector', ''),
                'button_text': pagination.get('button_text', 'Load More'),  # NEW!
                'wait_after_click': 2
            }

        elif approach['style'] == 'infinite':
            approach['implementation'] = {
                'type': 'scroll',
                'trigger_distance': 200,  # pixels from bottom
                'max_scrolls': 50,
                'pause_time': 2
            }

        return approach

    def _extract_pagination_params(self, report: Dict) -> Dict:
        """Extract actual pagination parameters from URLs"""
        params = {}

        # Look through captured network requests for pagination patterns
        for request in report.get('captured_data', {}).get('network_log', []):
            url = request.get('url', '')
            if 'page=' in url:
                params['page_param'] = 'page'
            elif 'offset=' in url:
                params['offset_param'] = 'offset'
            elif 'start=' in url:
                params['start_param'] = 'start'

        return params

    def _design_rate_limit_strategy(self, report: Dict) -> Dict:
        """Design rate limiting based on ACTUAL server behavior"""

        # Get actual metrics from reconnaissance
        network_stats = report.get('network_summary', {}).get('statistics', {})
        avg_response_time = network_stats.get('avg_response_time', 0)
        rate_limit_detected = bool(report.get('network_summary', {}).get('potential_rate_limits'))

        strategy = {
            'enabled': True,  # Always be respectful!

            # Base delay on actual response times
            'base_delay': self._calculate_safe_delay(avg_response_time, rate_limit_detected),

            # Specific discoveries
            'discovered_limits': {
                'rate_headers_found': rate_limit_detected,
                'avg_server_response': f"{avg_response_time:.0f}ms" if avg_response_time else "unknown",
                'endpoints_with_limits': list(report.get('network_summary', {}).get('potential_rate_limits', {}).keys())
            },

            # Adaptive strategy
            'adaptive_config': {
                'enabled': rate_limit_detected or avg_response_time > 1000,
                'backoff_multiplier': 2 if rate_limit_detected else 1.5,
                'max_delay': 10,  # seconds
                'respect_retry_after': True
            },

            # Headers to monitor (if found)
            'monitor_headers': [
                'x-ratelimit-remaining',
                'x-ratelimit-reset',
                'retry-after',
                'x-rate-limit-limit'
            ] if rate_limit_detected else []
        }

        return strategy

    def _calculate_safe_delay(self, avg_response_time: float, rate_limit_detected: bool) -> float:
        """Calculate safe delay based on server behavior"""
        if rate_limit_detected:
            return 2.0  # Be extra careful
        elif avg_response_time > 1000:
            return 1.5  # Slow server, be nice
        elif avg_response_time > 500:
            return 1.0  # Normal delay
        else:
            return 0.5  # Fast server can handle more

    def _design_error_handling(self, report: Dict) -> List[Dict]:
        """Design error handling based on ACTUAL errors encountered"""
        strategies = []

        # Check what errors we actually hit during recon
        encountered_errors = set()
        for result in report.get('liberation_results', []):
            if not result.get('success') and result.get('error'):
                encountered_errors.add(result['error'])

        # Base strategies everyone needs
        strategies.extend([
            {
                'error_type': 'network_timeout',
                'strategy': 'retry_with_backoff',
                'max_retries': 3,
                'encountered': 'timeout' in str(encountered_errors).lower()
            },
            {
                'error_type': 'rate_limit',
                'strategy': 'exponential_backoff',
                'initial_wait': 60,
                'encountered': bool(report.get('network_summary', {}).get('potential_rate_limits'))
            }
        ])

        # Add based on ACTUAL discoveries
        if report.get('discovered_features', {}).get('uses_javascript'):
            strategies.append({
                'error_type': 'element_not_found',
                'strategy': 'wait_and_retry',
                'wait_time': 5,
                'selectors_to_wait_for': list(self._generate_selectors(report).values())[:3]  # Top 3
            })

        # Cloudflare/protection detected?
        if any('cloudflare' in barrier.lower() for barrier in report.get('access_barriers', [])):
            strategies.append({
                'error_type': 'cloudflare_challenge',
                'strategy': 'use_undetected_chromedriver',
                'alternative': 'implement_solver'
            })

        # 404s from network log?
        error_codes = [r.get('status') for r in report.get('network_summary', {}).get('error_responses', [])]
        if 404 in error_codes:
            strategies.append({
                'error_type': '404_not_found',
                'strategy': 'verify_url_patterns',
                'discovered_pattern': report.get('url_patterns', {})
            })

        return strategies

    def _design_testing_strategy(self, report: Dict) -> Dict:
        """Design tests based on ACTUAL discoveries"""

        # Get actual things to test
        discovered_selectors = self._generate_selectors(report)
        api_endpoints = report.get('api_endpoints', [])
        forms_found = report.get('forms', [])

        test_cases = [
            {
                'name': 'connectivity_test',
                'description': f'Verify {report.get("url")} is accessible',
                'url': report.get('url'),
                'expected_status': 200,
                'critical': True
            }
        ]

        # Add selector tests for ACTUAL selectors
        if discovered_selectors:
            test_cases.append({
                'name': 'selector_validation',
                'description': 'Verify discovered selectors still work',
                'selectors_to_test': list(discovered_selectors.items())[:5],  # Test top 5
                'critical': True
            })

        # API endpoint tests
        if api_endpoints:
            test_cases.append({
                'name': 'api_availability',
                'description': 'Verify API endpoints still respond',
                'endpoints_to_test': api_endpoints[:3],
                'expected_response': 'json',
                'critical': True
            })

        # Form functionality tests
        if forms_found:
            test_cases.append({
                'name': 'form_functionality',
                'description': 'Verify forms accept input',
                'forms_to_test': [{'action': f.get('action'), 'method': f.get('method')}
                                  for f in forms_found[:2]],
                'critical': False
            })

        return {
            'test_cases': test_cases,
            'validation_data': {
                'sample_urls': self._extract_sample_urls(report),
                'expected_elements': discovered_selectors,
                'response_times': report.get('network_summary', {}).get('statistics', {})
            },
            'monitoring': {
                'check_frequency': 'daily' if len(test_cases) > 3 else 'weekly',
                'alert_on_failure': True,
                'baseline_metrics': {
                    'avg_response_time': report.get('network_summary', {}).get('statistics', {}).get(
                        'avg_response_time', 0),
                    'element_count': report.get('discovered_features', {}).get('total_elements', 0)
                }
            }
        }

    def _extract_sample_urls(self, report: Dict) -> List[str]:
        """Extract sample URLs for testing"""
        urls = set()

        # From downloadable content
        for item in report.get('downloadable_content', [])[:3]:
            if item.get('url'):
                urls.add(item['url'])

        # From API endpoints
        urls.update(report.get('api_endpoints', [])[:2])

        return list(urls)

    def _design_auth_strategy(self, report: Dict) -> Dict:
        """Design auth strategy based on ACTUAL forms/methods found"""

        # Check if login is needed
        has_login = report.get('discovered_features', {}).get('has_login', False)
        auth_endpoints = [ep for ep in report.get('api_endpoints', []) if 'auth' in ep.lower()]

        if not has_login and not auth_endpoints:
            return {
                'required': False,
                'reason': 'No authentication detected'
            }

        # Find actual login forms
        login_forms = []
        for form in report.get('forms', []):
            inputs = {inp.get('name', ''): inp.get('type', '') for inp in form.get('inputs', [])}
            if 'password' in inputs.values() or 'password' in str(inputs).lower():
                login_forms.append({
                    'action': form.get('action'),
                    'method': form.get('method'),
                    'fields': inputs
                })

        strategy = {
            'required': True,
            'discovered_methods': []
        }

        # Form-based auth
        if login_forms:
            strategy['discovered_methods'].append({
                'type': 'form_based',
                'forms': login_forms,
                'implementation': 'selenium_form_fill' if report.get('discovered_features', {}).get(
                    'uses_javascript') else 'requests_session'
            })

        # API auth
        if auth_endpoints:
            strategy['discovered_methods'].append({
                'type': 'api_based',
                'endpoints': auth_endpoints,
                'likely_method': 'bearer_token' if any('oauth' in ep for ep in auth_endpoints) else 'api_key'
            })

        # Cookie-based (from captured data)
        auth_cookies = [c for c in report.get('baseline', {}).get('cookies', [])
                        if any(term in c.get('name', '').lower() for term in ['auth', 'session', 'token'])]
        if auth_cookies:
            strategy['discovered_methods'].append({
                'type': 'cookie_based',
                'cookie_names': [c['name'] for c in auth_cookies],
                'persistence': 'check_expiry'
            })

        # Choose primary method
        strategy['recommended_method'] = strategy['discovered_methods'][0] if strategy['discovered_methods'] else {
            'type': 'unknown'}

        return strategy

    # ////

    def _save_comprehensive_report(self, report: Dict):
        """Save report in essential formats - SIMPLIFIED"""

        try:
            # Create session directory
            session_id = report.get('metadata', {}).get('analysis_id', datetime.now().strftime('%Y%m%d_%H%M%S'))
            session_dir = self.base_path / 'recon_reports' / session_id
            session_dir.mkdir(parents=True, exist_ok=True)

            # Simple structure: just data and screenshots
            (session_dir / 'screenshots').mkdir(exist_ok=True)

            self.logger.info(f"[REPORT] Saving to: {session_dir}")

            # 1. Save COMPLETE JSON report (single source of truth)
            json_path = session_dir / 'full_report.json'
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)
            self.logger.info(f"[REPORT] Complete data saved: {json_path}")

            # 2. Generate actionable outputs
            markdown_content = self._generate_markdown_report(report)
            markdown_path = session_dir / 'README.txt.md'
            markdown_path.write_text(markdown_content, encoding='utf-8')

            # 3. Save scraper blueprint (the GOAL of all this!)
            blueprint_path = session_dir / 'scraper_blueprint.yaml'
            with open(blueprint_path, 'w', encoding='utf-8') as f:
                yaml.dump(report.get('scraper_blueprint', {}), f, default_flow_style=False)

            # 4. Copy screenshots using the NEW structure
            screenshots_copied = self._copy_screenshots_simple(report, session_dir)
            self.logger.info(f"[REPORT] Copied {screenshots_copied} screenshots")

            # 5. Save code template if generated
            if 'code_template' in report.get('scraper_blueprint', {}):
                code_path = session_dir / 'scraper_template.py'
                code_path.write_text(report['scraper_blueprint']['code_template'], encoding='utf-8')
                self.logger.info("[REPORT] Code template saved")

            # 6. Update report with paths
            report['save_location'] = str(session_dir)
            report['files_created'] = {
                'report': str(json_path),
                'readme': str(markdown_path),
                'blueprint': str(blueprint_path),
                'session_dir': str(session_dir)
            }

            self.logger.info(f"[REPORT] Report saved successfully to: {session_dir}")

        except Exception as e:
            self.logger.error(f"[REPORT] Error saving report: {e}")
            raise

    def _copy_screenshots_simple(self, report: Dict, session_dir: Path) -> int:
        """Simple screenshot copying from artifacts"""
        copied = 0
        screenshots_dir = session_dir / 'screenshots'

        # Copy from artifacts.screenshots (our single source of truth!)
        for screenshot_info in report.get('artifacts', {}).get('screenshots', []):
            src_path = Path(screenshot_info.get('path', ''))

            if src_path.exists():
                dst_path = screenshots_dir / src_path.name
                try:
                    shutil.copy2(src_path, dst_path)
                    copied += 1
                except Exception as e:
                    self.logger.warning(f"Failed to copy {src_path.name}: {e}")

        return copied
