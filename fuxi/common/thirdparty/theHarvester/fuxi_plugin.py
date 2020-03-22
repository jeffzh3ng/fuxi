#!/usr/bin/env python3
import argparse

from fuxi.common.thirdparty.theHarvester.discovery import *
from fuxi.common.thirdparty.theHarvester.discovery.constants import *
from fuxi.common.thirdparty.theHarvester.lib import hostchecker
from fuxi.common.thirdparty.theHarvester.lib import reportgraph
from fuxi.common.thirdparty.theHarvester.lib import stash
from fuxi.common.thirdparty.theHarvester.lib import statichtmlgenerator
from fuxi.common.thirdparty.theHarvester.lib.core import *
import asyncio
import datetime
import netaddr
import re
import sys
import tempfile

# Core.banner()


async def start(args):
    try:
        db = stash.StashManager()
        await db.do_init()
    except Exception:
        pass

    all_emails: list = []
    all_hosts: list = []
    all_ip: list = []
    dnsbrute = args.dns_brute
    dnslookup = args.dns_lookup
    dnsserver = args.dns_server
    dnstld = args.dns_tld
    engines = []
    filename: str = args.filename
    full: list = []
    ips: list = []
    google_dorking = args.google_dork
    host_ip: list = []
    limit: int = args.limit
    shodan = args.shodan
    start: int = args.start
    all_urls: list = []
    vhost: list = []
    virtual = args.virtual_host
    word: str = args.domain
    takeover_status = args.take_over
    use_proxy = args.proxies

    async def store(search_engine: Any, source: str, process_param: Any = None, store_host: bool = False,
                    store_emails: bool = False, store_ip: bool = False, store_people: bool = False,
                    store_data: bool = False, store_links: bool = False, store_results: bool = False) -> None:
        """
        Persist details into the database.
        The details to be stored is controlled by the parameters passed to the method.

        :param search_engine: search engine to fetch details from
        :param source: source against which the details (corresponding to the search engine) need to be persisted
        :param process_param: any parameters to be passed to the search engine
                              eg: Google needs google_dorking
        :param store_host: whether to store hosts
        :param store_emails: whether to store emails
        :param store_ip: whether to store IP address
        :param store_people: whether to store user details
        :param store_data: whether to fetch host from method get_data() and persist
        :param store_links: whether to store links
        :param store_results: whether to fetch details from get_results() and persist
        """
        await search_engine.process(use_proxy) if process_param is None else await \
            search_engine.process(process_param, use_proxy)
        db_stash = stash.StashManager()
        if source == 'suip':
            print(f'\033[94m[*] Searching {source[0].upper() + source[1:]} this module can take 10+ min but is worth '
                  f'it. \033[0m')
        else:
            print(f'\033[94m[*] Searching {source[0].upper() + source[1:]}. \033[0m')
        if store_host:
            host_names = filter(await search_engine.get_hostnames())
            full_hosts_checker = hostchecker.Checker(host_names)
            temp_hosts, temp_ips = await full_hosts_checker.check()
            ips.extend(temp_ips)
            full.extend(temp_hosts)
            all_hosts.extend(host_names)
            await db_stash.store_all(word, all_hosts, 'host', source)
        if store_emails:
            email_list = filter(await search_engine.get_emails())
            all_emails.extend(email_list)
            await db_stash.store_all(word, email_list, 'email', source)
        if store_ip:
            ips_list = await search_engine.get_ips()
            all_ip.extend(ips_list)
            await db_stash.store_all(word, all_ip, 'ip', source)
        if store_data:
            data = filter(await search_engine.get_data())
            all_hosts.extend(data)
            await db.store_all(word, all_hosts, 'host', source)
        if store_results:
            email_list, host_names, urls = await search_engine.get_results()
            all_emails.extend(email_list)
            host_names = filter(host_names)
            all_urls.extend(filter(urls))
            all_hosts.extend(host_names)
            await db.store_all(word, all_hosts, 'host', source)
            await db.store_all(word, all_emails, 'email', source)
        if store_people:
            people_list = await search_engine.get_people()
            await db_stash.store_all(word, people_list, 'people', source)
            if len(people_list) == 0:
                print('\n[*] No users found.\n\n')
            else:
                print('\n[*] Users found: ' + str(len(people_list)))
                print('---------------------')
                for usr in sorted(list(set(people_list))):
                    print(usr)
        if store_links:
            links = await search_engine.get_links()
            await db.store_all(word, links, 'name', engineitem)
            if len(links) == 0:
                print('\n[*] No links found.\n\n')
            else:
                print(f'\n[*] Links found: {len(links)}')
                print('---------------------')
                for link in sorted(list(set(links))):
                    print(link)

    stor_lst = []
    if args.source is not None:
        if args.source.lower() != 'all':
            engines = sorted(set(map(str.strip, args.source.split(','))))
        else:
            engines = Core.get_supportedengines()
        # Iterate through search engines in order
        if set(engines).issubset(Core.get_supportedengines()):
            print(f'\033[94m[*] Target: {word} \n \033[0m')

            for engineitem in engines:
                if engineitem == 'baidu':
                    from fuxi.common.thirdparty.theHarvester.discovery import baidusearch
                    try:
                        baidu_search = baidusearch.SearchBaidu(word, limit)
                        stor_lst.append(store(baidu_search, engineitem, store_host=True, store_emails=True))
                    except Exception:
                        pass

                elif engineitem == 'bing' or engineitem == 'bingapi':
                    from fuxi.common.thirdparty.theHarvester.discovery import bingsearch
                    try:
                        bing_search = bingsearch.SearchBing(word, limit, start)
                        bingapi = ''
                        if engineitem == 'bingapi':
                            bingapi += 'yes'
                        else:
                            bingapi += 'no'
                        stor_lst.append(
                            store(bing_search, 'bing', process_param=bingapi, store_host=True, store_emails=True))
                    except Exception as e:
                        if isinstance(e, MissingKey):
                            print(e)
                        else:
                            print(e)

                elif engineitem == 'bufferoverun':
                    from fuxi.common.thirdparty.theHarvester.discovery import bufferoverun
                    try:
                        bufferoverun_search = bufferoverun.SearchBufferover(word)
                        stor_lst.append(store(bufferoverun_search, engineitem, store_host=True, store_ip=True))
                    except Exception as e:
                        print(e)

                elif engineitem == 'certspotter':
                    from fuxi.common.thirdparty.theHarvester.discovery import certspottersearch
                    try:
                        certspotter_search = certspottersearch.SearchCertspoter(word)
                        stor_lst.append(store(certspotter_search, engineitem, None, store_host=True))
                    except Exception as e:
                        print(e)

                elif engineitem == 'crtsh':
                    try:
                        from fuxi.common.thirdparty.theHarvester.discovery import crtsh
                        crtsh_search = crtsh.SearchCrtsh(word)
                        stor_lst.append(store(crtsh_search, 'CRTsh', store_data=True))
                    except Exception as e:
                        print(f'\033[93m[!] A timeout occurred with crtsh, cannot find {args.domain}\n {e}\033[0m')

                elif engineitem == 'dnsdumpster':
                    try:
                        from fuxi.common.thirdparty.theHarvester.discovery import dnsdumpster
                        dns_dumpster_search = dnsdumpster.SearchDnsDumpster(word)
                        stor_lst.append(store(dns_dumpster_search, engineitem, store_host=True))
                    except Exception as e:
                        print(f'\033[93m[!] An error occurred with dnsdumpster: {e} \033[0m')

                elif engineitem == 'dogpile':
                    try:
                        from fuxi.common.thirdparty.theHarvester.discovery import dogpilesearch
                        dogpile_search = dogpilesearch.SearchDogpile(word, limit)
                        stor_lst.append(store(dogpile_search, engineitem, store_host=True, store_emails=True))
                    except Exception as e:
                        print(f'\033[93m[!] An error occurred with Dogpile: {e} \033[0m')

                elif engineitem == 'duckduckgo':
                    from fuxi.common.thirdparty.theHarvester.discovery import duckduckgosearch
                    duckduckgo_search = duckduckgosearch.SearchDuckDuckGo(word, limit)
                    stor_lst.append(store(duckduckgo_search, engineitem, store_host=True, store_emails=True))

                elif engineitem == 'github-code':
                    try:
                        from fuxi.common.thirdparty.theHarvester.discovery import githubcode
                        github_search = githubcode.SearchGithubCode(word, limit)
                        stor_lst.append(store(github_search, engineitem, store_host=True, store_emails=True))
                    except MissingKey as ex:
                        print(ex)
                    else:
                        pass

                elif engineitem == 'exalead':
                    from fuxi.common.thirdparty.theHarvester.discovery import exaleadsearch
                    exalead_search = exaleadsearch.SearchExalead(word, limit, start)
                    stor_lst.append(store(exalead_search, engineitem, store_host=True, store_emails=True))

                elif engineitem == 'google':
                    from fuxi.common.thirdparty.theHarvester.discovery import googlesearch
                    google_search = googlesearch.SearchGoogle(word, limit, start)
                    stor_lst.append(store(google_search, engineitem, process_param=google_dorking, store_host=True,
                                          store_emails=True))

                elif engineitem == 'hunter':
                    from fuxi.common.thirdparty.theHarvester.discovery import huntersearch
                    # Import locally or won't work.
                    try:
                        hunter_search = huntersearch.SearchHunter(word, limit, start)
                        stor_lst.append(store(hunter_search, engineitem, store_host=True, store_emails=True))
                    except Exception as e:
                        if isinstance(e, MissingKey):
                            print(e)
                        else:
                            pass

                elif engineitem == 'intelx':
                    from fuxi.common.thirdparty.theHarvester.discovery import intelxsearch
                    # Import locally or won't work.
                    try:
                        intelx_search = intelxsearch.SearchIntelx(word, limit)
                        stor_lst.append(store(intelx_search, engineitem, store_host=True, store_emails=True))
                    except Exception as e:
                        if isinstance(e, MissingKey):
                            print(e)
                        else:
                            print(f'An exception has occurred in Intelx search: {e}')

                elif engineitem == 'linkedin':
                    from fuxi.common.thirdparty.theHarvester.discovery import linkedinsearch
                    linkedin_search = linkedinsearch.SearchLinkedin(word, limit)
                    stor_lst.append(store(linkedin_search, engineitem, store_people=True))

                elif engineitem == 'linkedin_links':
                    from fuxi.common.thirdparty.theHarvester.discovery import linkedinsearch
                    linkedin_links_search = linkedinsearch.SearchLinkedin(word, limit)
                    stor_lst.append(store(linkedin_links_search, 'linkedin', store_links=True))

                elif engineitem == 'netcraft':
                    from fuxi.common.thirdparty.theHarvester.discovery import netcraft
                    netcraft_search = netcraft.SearchNetcraft(word)
                    stor_lst.append(store(netcraft_search, engineitem, store_host=True))

                elif engineitem == 'otx':
                    from fuxi.common.thirdparty.theHarvester.discovery import otxsearch
                    try:
                        otxsearch_search = otxsearch.SearchOtx(word)
                        stor_lst.append(store(otxsearch_search, engineitem, store_host=True, store_ip=True))
                    except Exception as e:
                        print(e)

                elif engineitem == 'securityTrails':
                    from fuxi.common.thirdparty.theHarvester.discovery import securitytrailssearch
                    try:
                        securitytrails_search = securitytrailssearch.SearchSecuritytrail(word)
                        stor_lst.append(store(securitytrails_search, engineitem, store_host=True, store_ip=True))
                    except Exception as e:
                        if isinstance(e, MissingKey):
                            print(e)
                        else:
                            pass

                elif engineitem == 'suip':
                    from fuxi.common.thirdparty.theHarvester.discovery import suip
                    try:
                        suip_search = suip.SearchSuip(word)
                        stor_lst.append(store(suip_search, engineitem, store_host=True))
                    except Exception as e:
                        print(e)

                elif engineitem == 'spyse':
                    from fuxi.common.thirdparty.theHarvester.discovery import spyse
                    try:
                        spyse_search = spyse.SearchSpyse(word)
                        stor_lst.append(store(spyse_search, engineitem, store_host=True, store_ip=True))
                    except Exception as e:
                        print(e)

                elif engineitem == 'threatcrowd':
                    from fuxi.common.thirdparty.theHarvester.discovery import threatcrowd
                    try:
                        threatcrowd_search = threatcrowd.SearchThreatcrowd(word)
                        stor_lst.append(store(threatcrowd_search, engineitem, store_host=True))
                    except Exception as e:
                        print(e)

                elif engineitem == 'trello':
                    from fuxi.common.thirdparty.theHarvester.discovery import trello
                    # Import locally or won't work.
                    trello_search = trello.SearchTrello(word)
                    stor_lst.append(store(trello_search, engineitem, store_results=True))

                elif engineitem == 'twitter':
                    from fuxi.common.thirdparty.theHarvester.discovery import twittersearch
                    twitter_search = twittersearch.SearchTwitter(word, limit)
                    stor_lst.append(store(twitter_search, engineitem, store_people=True))

                elif engineitem == 'virustotal':
                    from fuxi.common.thirdparty.theHarvester.discovery import virustotal
                    virustotal_search = virustotal.SearchVirustotal(word)
                    stor_lst.append(store(virustotal_search, engineitem, store_host=True))

                elif engineitem == 'yahoo':

                    from fuxi.common.thirdparty.theHarvester.discovery import yahoosearch
                    yahoo_search = yahoosearch.SearchYahoo(word, limit)
                    stor_lst.append(store(yahoo_search, engineitem, store_host=True, store_emails=True))
        else:
            print('\033[93m[!] Invalid source.\n\n \033[0m')
            # sys.exit(1)

    async def worker(queue):
        while True:
            # Get a "work item" out of the queue.
            stor = await queue.get()
            try:
                await stor
                queue.task_done()
                # Notify the queue that the "work item" has been processed.
            except Exception:
                queue.task_done()

    async def handler(lst):
        queue = asyncio.Queue()

        for stor_method in lst:
            # enqueue the coroutines
            queue.put_nowait(stor_method)
        # Create five worker tasks to process the queue concurrently.
        tasks = []
        for i in range(5):
            task = asyncio.create_task(worker(queue))
            tasks.append(task)

        # Wait until the queue is fully processed.
        await queue.join()

        # Cancel our worker tasks.
        for task in tasks:
            task.cancel()
        # Wait until all worker tasks are cancelled.
        await asyncio.gather(*tasks, return_exceptions=True)

    await handler(lst=stor_lst)

    # Sanity check to see if all_emails and all_hosts are defined.
    try:
        all_emails
    except NameError:
        print('\n\n\033[93m[!] No emails found because all_emails is not defined.\n\n \033[0m')
        # sys.exit(1)
    try:
        all_hosts
    except NameError:
        print('\n\n\033[93m[!] No hosts found because all_hosts is not defined.\n\n \033[0m')
        # sys.exit(1)

    # Results
    if len(all_ip) == 0:
        print('\n[*] No IPs found.')
    else:
        print('\n[*] IPs found: ' + str(len(all_ip)))
        print('-------------------')
        # use netaddr as the list may contain ipv4 and ipv6 addresses
        ip_list = [netaddr.IPAddress(ip.strip()) for ip in set(all_ip)]
        ip_list.sort()
        print('\n'.join(map(str, ip_list)))

    if len(all_emails) == 0:
        print('\n[*] No emails found.')
    else:
        print('\n[*] Emails found: ' + str(len(all_emails)))
        print('----------------------')
        print(('\n'.join(sorted(list(set(all_emails))))))

    if len(all_hosts) == 0:
        print('\n[*] No hosts found.\n\n')
    else:
        print('\n[*] Hosts found: ' + str(len(all_hosts)))
        print('---------------------')
        all_hosts = sorted(list(set(all_hosts)))
        """full_host = hostchecker.Checker(all_hosts)
        full, ips = await full_host.check()"""
        db = stash.StashManager()
        full.sort(key=lambda el: el.split(':')[0])
        for host in full:
            host = str(host)
            print(host)
        host_ip = [netaddr_ip.format() for netaddr_ip in sorted([netaddr.IPAddress(ip) for ip in ips])]
        await db.store_all(word, host_ip, 'ip', 'DNS-resolver')
    length_urls = len(all_urls)
    if length_urls == 0:
        if len(engines) >= 1 and 'trello' in engines:
            print('\n[*] No Trello URLs found.')
    else:
        total = length_urls
        print('\n[*] Trello URLs found: ' + str(total))
        print('--------------------')
        for url in sorted(all_urls):
            print(url)

    # DNS brute force
    # dnsres = []
    if dnsbrute is True:
        print('\n[*] Starting DNS brute force.')
        a = dnssearch.DnsForce(word, dnsserver, verbose=True)
        a.process()
        # print('\n[*] Hosts found after DNS brute force:')
        # for y in res:
        # print('-------------------------------------')
        #    print(y)
        #   dnsres.append(y.split(':')[0])
        #    if y not in full:
        #        full.append(y)
        # db = stash.stash_manager()
        # db.store_all(word, dnsres, 'host', 'dns_bruteforce')

    # TakeOver Checking

    if takeover_status:
        print('\n[*] Performing subdomain takeover check')
        print('\n[*] Subdomain Takeover checking IS ACTIVE RECON')
        search_take = takeover.TakeOver(all_hosts)
        await search_take.process(proxy=use_proxy)

    # DNS reverse lookup
    dnsrev = []
    if dnslookup is True:
        print('\n[*] Starting active queries.')
        analyzed_ranges = []
        for entry in host_ip:
            print(entry)
            ip = entry.split(':')[0]
            ip_range = ip.split('.')
            ip_range[3] = '0/24'
            s = '.'
            ip_range = s.join(ip_range)
            if not analyzed_ranges.count(ip_range):
                print('[*] Performing reverse lookup in ' + ip_range)
                a = dnssearch.DnsReverse(ip_range, True)
                a.list()
                res = a.process()
                analyzed_ranges.append(ip_range)
            else:
                continue
            for entries in res:
                if entries.count(word):
                    dnsrev.append(entries)
                    if entries not in full:
                        full.append(entries)
        print('[*] Hosts found after reverse lookup (in target domain):')
        print('--------------------------------------------------------')
        for xh in dnsrev:
            print(xh)

    # DNS TLD expansion
    dnstldres = []
    if dnstld is True:
        print('[*] Starting DNS TLD expansion.')
        a = dnssearch.DnsTld(word, dnsserver, verbose=True)
        res = a.process()
        print('\n[*] Hosts found after DNS TLD expansion:')
        print('----------------------------------------')
        for y in res:
            print(y)
            dnstldres.append(y)
            if y not in full:
                full.append(y)

    # Virtual hosts search
    if virtual == 'basic':
        print('\n[*] Virtual hosts:')
        print('------------------')
        for l in host_ip:
            basic_search = bingsearch.SearchBing(l, limit, start)
            await basic_search.process_vhost()
            results = await basic_search.get_allhostnames()
            for result in results:
                result = re.sub(r'[[\<\/?]*[\w]*>]*', '', result)
                result = re.sub('<', '', result)
                result = re.sub('>', '', result)
                print((l + '\t' + result))
                vhost.append(l + ':' + result)
                full.append(l + ':' + result)
        vhost = sorted(set(vhost))
    else:
        pass

    # Shodan
    shodanres = []
    if shodan is True:
        import texttable
        tab = texttable.Texttable()
        header = ['IP address', 'Hostname', 'Org', 'Services:Ports', 'Technologies']
        tab.header(header)
        tab.set_cols_align(['c', 'c', 'c', 'c', 'c'])
        tab.set_cols_valign(['m', 'm', 'm', 'm', 'm'])
        tab.set_chars(['-', '|', '+', '#'])
        tab.set_cols_width([15, 20, 15, 15, 18])
        print('\033[94m[*] Searching Shodan. \033[0m')
        try:
            for ip in host_ip:
                print(('\tSearching for ' + ip))
                shodan = shodansearch.SearchShodan()
                rowdata = await shodan.search_ip(ip)
                await asyncio.sleep(2)
                tab.add_row(rowdata)
            printedtable = tab.draw()
            print(printedtable)
        except Exception as e:
            print(f'\033[93m[!] An error occurred with Shodan: {e} \033[0m')
    else:
        pass

    # Here we need to add explosion mode.
    # We have to take out the TLDs to do this.
    if args.dns_tld is not False:
        counter = 0
        for word in vhost:
            search = googlesearch.SearchGoogle(word, limit, counter)
            await search.process(google_dorking)
            emails = await search.get_emails()
            hosts = await search.get_hostnames()
            print(emails)
            print(hosts)
    else:
        pass

    # Reporting
    if filename != "":
        try:
            print('\n[*] Reporting started.')
            db = stash.StashManager()
            scanboarddata = await db.getscanboarddata()
            latestscanresults = await db.getlatestscanresults(word)
            previousscanresults = await db.getlatestscanresults(word, previousday=True)
            latestscanchartdata = await db.latestscanchartdata(word)
            scanhistorydomain = await db.getscanhistorydomain(word)
            pluginscanstatistics = await db.getpluginscanstatistics()
            generator = statichtmlgenerator.HtmlGenerator(word)
            HTMLcode = await generator.beginhtml()
            HTMLcode += await generator.generatelatestscanresults(latestscanresults)
            HTMLcode += await generator.generatepreviousscanresults(previousscanresults)
            graph = reportgraph.GraphGenerator(word)
            await graph.init_db()
            HTMLcode += await graph.drawlatestscangraph(word, latestscanchartdata)
            HTMLcode += await graph.drawscattergraphscanhistory(word, scanhistorydomain)
            HTMLcode += await generator.generatepluginscanstatistics(pluginscanstatistics)
            HTMLcode += await generator.generatedashboardcode(scanboarddata)
            HTMLcode += '<p><span style="color: #000000;">Report generated on ' + str(
                datetime.datetime.now()) + '</span></p>'
            HTMLcode += '''
               </body>
               </html>
               '''
            Html_file = open(f'{filename}.html' if '.html' not in filename else filename, 'w')
            Html_file.write(HTMLcode)
            Html_file.close()
            print('[*] Reporting finished.')
            print('[*] Saving files.')
        except Exception as e:
            print(e)
            print('\n\033[93m[!] An error occurred while creating the output file.\n\n \033[0m')
            # sys.exit(1)

        try:
            filename.rsplit('.', 1)[0] + '.xml'
            file = open(filename, 'w')
            file.write('<?xml version="1.0" encoding="UTF-8"?><theHarvester>')
            for x in all_emails:
                file.write('<email>' + x + '</email>')
            for x in full:
                host, ip = x.split(':') if ':' in x else (x, '')
                if ip and len(ip) > 3:
                    file.write(f'<host><ip>{ip}</ip><hostname>{host}</hostname></host>')
                else:
                    file.write(f'<host>{host}</host>')
            for x in vhost:
                host, ip = x.split(':') if ':' in x else (x, '')
                if ip and len(ip) > 3:
                    file.write(f'<vhost><ip>{ip} </ip><hostname>{host}</hostname></vhost>')
                else:
                    file.write(f'<vhost>{host}</vhost>')
            if shodanres != []:
                shodanalysis = []
                for x in shodanres:
                    res = x.split('SAPO')
                    file.write('<shodan>')
                    file.write('<host>' + res[0] + '</host>')
                    file.write('<port>' + res[2] + '</port>')
                    file.write('<banner><!--' + res[1] + '--></banner>')
                    reg_server = re.compile('Server:.*')
                    temp = reg_server.findall(res[1])
                    if temp:
                        shodanalysis.append(res[0] + ':' + temp[0])
                    file.write('</shodan>')
                if shodanalysis:
                    shodanalysis = sorted(set(shodanalysis))
                    file.write('<servers>')
                    for x in shodanalysis:
                        file.write('<server>' + x + '</server>')
                    file.write('</servers>')

            file.write('</theHarvester>')
            file.flush()
            file.close()
            print('[*] Files saved.')
        except Exception as er:
            print(f'\033[93m[!] An error occurred while saving the XML file: {er} \033[0m')
        print('\n\n')
        # sys.exit(0)


async def entry_point(args):
    try:
        await start(args)
        # await handler()
    except KeyboardInterrupt:
        print('\n\n\033[93m[!] ctrl+c detected from user, quitting.\n\n \033[0m')
    except Exception as error_entry_point:
        print(error_entry_point)
        # sys.exit(1)

def fuxi_theharvester(domain):
    filename = _temp_filepath()
    parser = argparse.ArgumentParser()
    source = "baidu,bing,bufferoverun, certspotter, crtsh, dnsdumpster, " \
             "duckduckgo, github-code, hunter, netcraft, securityTrails, " \
             "threatcrowd, trello, twitter, vhost, virustotal"
    parser.add_argument('-d', '--domain', default=domain)
    parser.add_argument('-l', '--limit', default=300, type=int)
    parser.add_argument('-S', '--start', default=0, type=int)
    parser.add_argument('-g', '--google-dork', default=False, action='store_true')
    parser.add_argument('-p', '--proxies', default=False, action='store_true')
    parser.add_argument('-s', '--shodan', default=False, action='store_true')
    parser.add_argument('-v', '--virtual-host', action='store_const', const='basic', default=False)
    parser.add_argument('-e', '--dns-server')
    parser.add_argument('-t', '--dns-tld', default=False)
    parser.add_argument('-r', '--take-over', default=False, action='store_true')
    parser.add_argument('-n', '--dns-lookup', default=False, action='store_true')
    parser.add_argument('-c', '--dns-brute', default=False, action='store_true')
    parser.add_argument('-f', '--filename', default=filename, type=str)
    parser.add_argument('-b', '--source', default=source)
    args = parser.parse_args(args=[])
    asyncio.run(entry_point(args))
    return filename


def _temp_filepath():
    seed = "1234567890abcdefghijklmnopqrstuvwxyz"
    filename = ''.join(random.sample(seed, 10))
    return tempfile.gettempdir() + "/" + filename
