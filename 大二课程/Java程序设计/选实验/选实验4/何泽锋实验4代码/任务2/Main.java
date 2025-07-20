import java.util.Arrays;
import java.util.Comparator;
import java.util.TreeMap;
import java.util.Scanner;
class Team extends Object
{
    public String name;
    public int Gold,Silver,Bronze;
    public Team(String name,int gold,int silver,int bronze){
        this.name=name;
        this.Gold=gold;
        this.Silver=silver;
        this.Bronze=bronze;
    }
    @Override
    public String toString(){
        return name+" "+Gold+" "+Silver+" "+Bronze;
    }
}
class TeamCompare implements Comparator<Team> {
    @Override
    public int compare(Team t1, Team t2) {
        return Integer.compare(t1.Silver, t2.Silver);
    }
}

public class Main {
    public static void main(String[] args) {
        TreeMap<Team, String> teams = new TreeMap<> (new TeamCompare());
        teams.put(new Team("CHN", 201, 111, 71),"CHN");
        teams.put( new Team("JPN", 52, 67, 69),"JPN");
        teams.put( new Team("KOR", 42, 59, 89),"KOR");
        teams.put( new Team("IND", 28, 38, 41),"IND");
        teams.put( new Team("UZB", 22, 18, 31),"UZB");
        teams.put( new Team("TPE", 19, 20, 28),"TPE");
        teams.put( new Team("IRI", 13, 21, 20),"IRI");
        teams.put( new Team("THA", 12, 14, 32),"THA");
        teams.put( new Team("BRN", 12, 3, 5),"BRN");
        teams.put( new Team("PRK", 11, 18, 10),"PRK");
        System.out.println("使用Comparator接口");
        System.out.println("按照银牌数量从小到大排序的队伍信息：");
        for (String s : teams.values()) {
            System.out.println(s);
        }
    }
}